"""Abstract base class for agent adapters."""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator


class AgentAdapter(ABC):
    """Interface that all agent adapters must implement."""

    @abstractmethod
    async def connect(self) -> None:
        """Initialize the client connection."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up the client connection."""

    @abstractmethod
    def get_context(self) -> dict[str, Any]:
        """Return metadata about the adapter (model, provider, available tools)."""

    @abstractmethod
    async def query(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> dict[str, Any]:
        """Send a message and return the full response."""

    @abstractmethod
    async def query_stream(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Send a message and stream response events."""

    async def __aenter__(self) -> "AgentAdapter":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disconnect()
