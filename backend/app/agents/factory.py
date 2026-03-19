"""Factory for creating the configured agent adapter."""

from .base import AgentAdapter
from .bedrock import BedrockAdapter
from .claude import ClaudeAdapter
from ..config import config


def create_agent_adapter() -> AgentAdapter:
    """Return the adapter selected by config.agent_provider (claude | bedrock)."""
    provider = config.agent_provider.lower()

    if provider == "bedrock":
        bedrock_cfg = config.bedrock
        return BedrockAdapter(
            region=bedrock_cfg.region,
            model_id=bedrock_cfg.model_id,
            temperature=bedrock_cfg.temperature,
            max_tokens=bedrock_cfg.max_tokens,
            top_p=bedrock_cfg.top_p,
        )

    return ClaudeAdapter()
