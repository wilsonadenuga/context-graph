# Agents Package

Adapter pattern to switch between Claude and AWS Bedrock via `AGENT_PROVIDER=claude|bedrock`.

## New files
- `base.py` — abstract adapter interface
- `tools.py` — all tool functions, system prompt, tool registry
- `claude.py` — Claude SDK adapter
- `bedrock.py` — Bedrock Converse API adapter
- `factory.py` — picks adapter based on `AGENT_PROVIDER` env var

## Changed files
- `backend/app/agent.py` — reduced to thin wrapper delegating to the adapter
- `backend/app/config.py` — added `BedrockConfig`
- `backend/pyproject.toml` — added `boto3>=1.26.0`
