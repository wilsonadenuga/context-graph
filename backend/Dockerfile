FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# --- Dependencies Install Stage ---
FROM base AS deps
WORKDIR /app

COPY backend/pyproject.toml .
COPY backend/uv.lock .
COPY backend/entrypoint.sh .

RUN uv sync --frozen --no-dev --no-install-project

# --- Runner Stage ---
FROM base AS runner
WORKDIR /app

COPY --from=deps /app/.venv /app/.venv
COPY --from=deps /app/entrypoint.sh .
COPY backend/app ./app
COPY backend/scripts ./scripts
COPY cypher/schema.cypher ./cypher/schema.cypher
ENV PATH="/app/.venv/bin:$PATH"

RUN chmod +x entrypoint.sh
EXPOSE 8081

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser



USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
