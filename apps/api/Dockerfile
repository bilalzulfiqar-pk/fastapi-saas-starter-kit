FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /workspace/apps/api

COPY apps/api /workspace/apps/api

RUN uv pip install --system -e ".[dev]"

EXPOSE 8000

