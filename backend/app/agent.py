"""Backward-compatible entry point for ContextGraphAgent."""

from typing import Any

from .agents.factory import create_agent_adapter


class ContextGraphAgent:
    """Manages an agent session. Delegates to the adapter selected by AGENT_PROVIDER."""

    def __init__(self):
        self.adapter = create_agent_adapter()

    async def __aenter__(self) -> "ContextGraphAgent":
        await self.adapter.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.adapter.disconnect()

    async def query(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> dict[str, Any]:
        return await self.adapter.query(message, conversation_history)

    async def query_stream(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ):
        async for event in self.adapter.query_stream(message, conversation_history):
            yield event
