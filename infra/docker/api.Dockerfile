# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /usr/local/bin/uv

WORKDIR /app

# Cache deps in a separate layer
COPY pyproject.toml uv.lock* ./
COPY apps/api/pyproject.toml apps/api/
COPY packages/cv/pyproject.toml packages/cv/
COPY packages/ontology/pyproject.toml packages/ontology/
COPY packages/dataset/pyproject.toml packages/dataset/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --package phongthuy-api || \
    uv sync --no-install-project --package phongthuy-api

# Copy source
COPY apps/api/src apps/api/src
COPY packages/cv/src packages/cv/src
COPY packages/ontology/src packages/ontology/src
COPY packages/dataset/src packages/dataset/src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package phongthuy-api

EXPOSE 8000

CMD ["uv", "run", "--package", "phongthuy-api", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
