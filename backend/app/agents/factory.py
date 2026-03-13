"""Factory for creating the configured agent adapter."""

import os

from .base import AgentAdapter
from .bedrock import BedrockAdapter
from .claude import ClaudeAdapter


def create_agent_adapter() -> AgentAdapter:
    """Return the adapter selected by the AGENT_PROVIDER env var (claude | bedrock).

    Claude is the default. Switch to Bedrock by setting:
        AGENT_PROVIDER=bedrock
        AWS_REGION=us-east-1          # optional, defaults to us-east-1
        BEDROCK_MODEL_ID=...          # optional, defaults to claude-sonnet-4-5
    """
    provider = os.getenv("AGENT_PROVIDER", "claude").lower()

    if provider == "bedrock":
        return BedrockAdapter(
            region=os.getenv("AWS_REGION", "us-east-1"),
            model_id=os.getenv(
                "BEDROCK_MODEL_ID",
                "us.anthropic.claude-sonnet-4-5-20251001-v2:0",
            ),
        )

    return ClaudeAdapter()
