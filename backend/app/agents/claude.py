"""Claude API adapter using claude_agent_sdk."""

import json
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, create_sdk_mcp_server
from claude_agent_sdk import tool as sdk_tool

from .base import AgentAdapter
from .tools import (
    AVAILABLE_TOOLS,
    CONTEXT_GRAPH_SYSTEM_PROMPT,
    TOOL_DEFINITIONS,
    build_agent_message,
)


def _create_mcp_server():
    """Dynamically wrap tool functions and create the MCP server."""
    wrapped_tools = [
        sdk_tool(td.name, td.description, td.parameters)(td.fn) for td in TOOL_DEFINITIONS
    ]
    return create_sdk_mcp_server(
        name="context-graph",
        version="1.0.0",
        tools=wrapped_tools,
    )


class ClaudeAdapter(AgentAdapter):
    """Adapter that uses the Claude Agent SDK with MCP tools."""

    def __init__(self):
        self.client: ClaudeSDKClient | None = None

    def get_context(self) -> dict[str, Any]:
        return {
            "system_prompt": CONTEXT_GRAPH_SYSTEM_PROMPT,
            "model": "claude-sonnet-4-20250514",
            "available_tools": AVAILABLE_TOOLS,
            "mcp_server": "context-graph",
            "provider": "claude",
        }

    async def connect(self) -> None:
        mcp_server = _create_mcp_server()
        allowed_tools = [f"mcp__graph__{name}" for name in AVAILABLE_TOOLS]
        options = ClaudeAgentOptions(
            system_prompt=CONTEXT_GRAPH_SYSTEM_PROMPT,
            mcp_servers={"graph": mcp_server},
            allowed_tools=allowed_tools,
        )
        self.client = ClaudeSDKClient(options=options)
        await self.client.connect()

    async def disconnect(self) -> None:
        if self.client:
            await self.client.disconnect()

    async def query(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> dict[str, Any]:
        if not self.client:
            raise RuntimeError("Adapter not connected. Use 'async with' context manager.")

        await self.client.query(build_agent_message(message, conversation_history))

        response_text = ""
        tool_calls = []

        async for msg in self.client.receive_response():
            if hasattr(msg, "content"):
                for block in msg.content:
                    if hasattr(block, "text"):
                        response_text += block.text
                    elif hasattr(block, "name"):
                        tool_calls.append(
                            {
                                "name": block.name,
                                "input": block.input if hasattr(block, "input") else {},
                            }
                        )

        return {"response": response_text, "tool_calls": tool_calls, "decisions_made": []}

    async def query_stream(  # type: ignore[override]
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ):
        if not self.client:
            raise RuntimeError("Adapter not connected. Use 'async with' context manager.")

        yield {"type": "agent_context", "context": self.get_context()}

        await self.client.query(build_agent_message(message, conversation_history))

        tool_calls = []
        tool_id_to_name: dict[str, str] = {}

        async for msg in self.client.receive_response():
            msg_type = type(msg).__name__

            if msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    if type(block).__name__ == "ToolResultBlock":
                        tool_use_id = getattr(block, "tool_use_id", None)
                        block_content = getattr(block, "content", None)

                        print(f"[DEBUG] ToolResultBlock - tool_use_id: {tool_use_id}")

                        if tool_use_id:
                            parsed_output = None
                            if isinstance(block_content, list):
                                for item in block_content:
                                    if isinstance(item, dict) and item.get("type") == "text":
                                        try:
                                            parsed_output = json.loads(item.get("text", "{}"))
                                        except json.JSONDecodeError:
                                            parsed_output = item.get("text")
                                        break
                                    elif hasattr(item, "text"):
                                        try:
                                            parsed_output = json.loads(item.text)
                                        except json.JSONDecodeError:
                                            parsed_output = item.text
                                        break
                            elif isinstance(block_content, str):
                                try:
                                    parsed_output = json.loads(block_content)
                                except json.JSONDecodeError:
                                    parsed_output = block_content

                            tool_name = tool_id_to_name.get(tool_use_id, "unknown")
                            print(
                                f"[DEBUG] Yielding tool_result: name={tool_name}, output_type={type(parsed_output)}"
                            )

                            yield {
                                "type": "tool_result",
                                "name": tool_name,
                                "output": parsed_output,
                            }
                continue

            if hasattr(msg, "content"):
                for block in msg.content:
                    if hasattr(block, "text"):
                        yield {"type": "text", "content": block.text}
                    elif hasattr(block, "name"):
                        tool_id = getattr(block, "id", None)
                        tool_call = {
                            "name": block.name,
                            "input": block.input if hasattr(block, "input") else {},
                        }
                        tool_calls.append(tool_call)
                        if tool_id:
                            tool_id_to_name[tool_id] = block.name
                        yield {"type": "tool_use", **tool_call}

        yield {"type": "done", "tool_calls": tool_calls, "decisions_made": []}
