# Bedrock Adapter

Adapter for using Claude via AWS Bedrock instead of Anthropic's API directly.

## Key Decisions

### 1. aioboto3 for True Async
Uses `aioboto3` instead of `boto3` for native async I/O without thread pool overhead.

### 2. Manual Tool Execution Loop
Bedrock requires manual tool handling:
1. Send message with tool definitions
2. Get response with `stopReason: "tool_use"`
3. Execute tools via `_execute_tool()`
4. Send results back to Bedrock
5. Loop until final response

### 3. Required Fields in Tool Schema
Parameters without defaults are marked as required in the JSON schema for better Bedrock validation.

### 4. Hybrid Streaming
- Use `converse_stream` for real-time text tokens
- Fall back to `converse` (non-streaming) to get complete tool metadata
- Trade-off: Extra API call for tools, but necessary for full tool data

### 5. Throttling Retry Only
Only handles `ThrottlingException` with exponential backoff (2s, 4s, 8s). Other errors bubble up naturally.

### 6. Configurable Inference
Exposes `temperature`, `max_tokens`, `top_p` via environment variables.

## Configuration

```bash
AGENT_PROVIDER=bedrock
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20251001-v2:0

# Inference parameters (optional)
BEDROCK_TEMPERATURE=1.0    # Randomness (0.0=deterministic, 1.0=creative)
BEDROCK_MAX_TOKENS=4096    # Maximum response length
BEDROCK_TOP_P=0.999        # Diversity threshold (lower=more focused)
```

AWS credentials via IAM role (production), credentials file, or environment variables.

## Response Format

Matches Claude SDK adapter exactly:

**Non-streaming:**
```python
{"response": "text", "tool_calls": [...], "decisions_made": []}
```

**Streaming:**
```python
{"type": "agent_context", "context": {...}}
{"type": "text", "content": "chunk"}
{"type": "tool_use", "name": "...", "input": {...}}
{"type": "tool_result", "name": "...", "output": {...}}
{"type": "done", "tool_calls": [...], "decisions_made": []}
```
