"""Bedrock adapter using boto3 Converse API with manual tool execution loop."""

import asyncio
import json
from typing import Any

import boto3

from .base import AgentAdapter
from .tools import (
    AVAILABLE_TOOLS,
    CONTEXT_GRAPH_SYSTEM_PROMPT,
    TOOL_DEFINITIONS,
    TOOL_REGISTRY,
    build_agent_message,
)


def _python_type_to_json_schema_type(t) -> str:
    return {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }.get(t, "string")


def _build_tool_config() -> dict:
    """Convert ToolDefinitions to Bedrock's toolConfig format."""
    tools = []
    for td in TOOL_DEFINITIONS:
        properties = {}
        for param_name, schema in td.parameters.items():
            if isinstance(schema, type):
                properties[param_name] = {"type": _python_type_to_json_schema_type(schema)}
            elif isinstance(schema, dict):
                prop = {}
                t = schema.get("type")
                if t is not None:
                    prop["type"] = _python_type_to_json_schema_type(t) if isinstance(t, type) else t
                if "description" in schema:
                    prop["description"] = schema["description"]
                properties[param_name] = prop

        tools.append(
            {
                "toolSpec": {
                    "name": td.name,
                    "description": td.description,
                    "inputSchema": {"json": {"type": "object", "properties": properties}},
                }
            }
        )
    return {"tools": tools}


async def _execute_tool(name: str, input_data: dict) -> str:
    """Execute a tool by name and return the result as a string."""
    tool_def = TOOL_REGISTRY.get(name)
    if not tool_def:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = await tool_def.fn(input_data)
        content = result.get("content", [])
        if content:
            return content[0].get("text", "")
        return ""
    except Exception as e:
        return json.dumps({"error": str(e)})


class BedrockAdapter(AgentAdapter):
    """Adapter that uses the AWS Bedrock Converse API with a manual tool execution loop."""

    def __init__(
        self,
        region: str = "us-east-1",
        model_id: str = "us.anthropic.claude-sonnet-4-5-20251001-v2:0",
    ):
        self.region = region
        self.model_id = model_id
        self.client = None
        self._tool_config = _build_tool_config()

    def get_context(self) -> dict[str, Any]:
        return {
            "system_prompt": CONTEXT_GRAPH_SYSTEM_PROMPT,
            "model": self.model_id,
            "available_tools": AVAILABLE_TOOLS,
            "provider": "bedrock",
        }

    async def connect(self) -> None:
        self.client = await asyncio.to_thread(
            boto3.client, "bedrock-runtime", region_name=self.region
        )

    async def disconnect(self) -> None:
        pass

    def _build_messages(
        self, message: str, conversation_history: list[dict[str, str]] | None
    ) -> list:
        return [
            {
                "role": "user",
                "content": [{"text": build_agent_message(message, conversation_history)}],
            }
        ]

    async def query(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> dict[str, Any]:
        messages = self._build_messages(message, conversation_history)
        tool_calls = []

        while True:
            response = await asyncio.to_thread(
                self.client.converse,
                modelId=self.model_id,
                system=[{"text": CONTEXT_GRAPH_SYSTEM_PROMPT}],
                messages=messages,
                toolConfig=self._tool_config,
            )

            output_message = response["output"]["message"]
            messages.append(output_message)
            stop_reason = response["stopReason"]

            if stop_reason == "tool_use":
                tool_results = []
                for block in output_message["content"]:
                    if "toolUse" in block:
                        tool_use = block["toolUse"]
                        name = tool_use["name"]
                        input_data = tool_use["input"]
                        tool_use_id = tool_use["toolUseId"]

                        tool_calls.append({"name": name, "input": input_data})
                        result_text = await _execute_tool(name, input_data)

                        tool_results.append(
                            {
                                "toolResult": {
                                    "toolUseId": tool_use_id,
                                    "content": [{"text": result_text}],
                                }
                            }
                        )

                messages.append({"role": "user", "content": tool_results})
            else:
                response_text = "".join(
                    block["text"] for block in output_message["content"] if "text" in block
                )
                return {"response": response_text, "tool_calls": tool_calls, "decisions_made": []}

    async def query_stream(  # type: ignore[override]
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ):
        messages = self._build_messages(message, conversation_history)
        tool_calls = []

        yield {"type": "agent_context", "context": self.get_context()}

        while True:
            response = await asyncio.to_thread(
                self.client.converse,
                modelId=self.model_id,
                system=[{"text": CONTEXT_GRAPH_SYSTEM_PROMPT}],
                messages=messages,
                toolConfig=self._tool_config,
            )

            output_message = response["output"]["message"]
            messages.append(output_message)
            stop_reason = response["stopReason"]

            if stop_reason == "tool_use":
                tool_results = []
                for block in output_message["content"]:
                    if "toolUse" in block:
                        tool_use = block["toolUse"]
                        name = tool_use["name"]
                        input_data = tool_use["input"]
                        tool_use_id = tool_use["toolUseId"]

                        tool_call = {"name": name, "input": input_data}
                        tool_calls.append(tool_call)
                        yield {"type": "tool_use", **tool_call}

                        result_text = await _execute_tool(name, input_data)

                        try:
                            parsed_output = json.loads(result_text)
                        except json.JSONDecodeError:
                            parsed_output = result_text

                        yield {"type": "tool_result", "name": name, "output": parsed_output}

                        tool_results.append(
                            {
                                "toolResult": {
                                    "toolUseId": tool_use_id,
                                    "content": [{"text": result_text}],
                                }
                            }
                        )

                messages.append({"role": "user", "content": tool_results})
            else:
                for block in output_message["content"]:
                    if "text" in block:
                        yield {"type": "text", "content": block["text"]}

                yield {"type": "done", "tool_calls": tool_calls, "decisions_made": []}
                break
