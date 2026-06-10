# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Treat PyPI hosts as TLS-insecure so corporate / VPN MITM proxies
    # whose cert chain isn't in the slim base image's trust store don't
    # break `uv sync`. Package integrity is still verified by uv via the
    # sha256 entries in uv.lock — this only relaxes transport-layer
    # verification, not artefact verification.
    UV_INSECURE_HOST="pypi.org files.pythonhosted.org"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /usr/local/bin/uv

WORKDIR /app

# Cache deps in a separate layer. Each package's pyproject.toml goes in
# first so a code-only change doesn't invalidate the deps layer.
COPY pyproject.toml uv.lock* ./
COPY apps/api/pyproject.toml apps/api/
COPY packages/cv/pyproject.toml packages/cv/
COPY packages/ontology/pyproject.toml packages/ontology/
COPY packages/dataset/pyproject.toml packages/dataset/
COPY packages/generator/pyproject.toml packages/generator/

# `phongthuy-ontology` and `phongthuy-generator` force-include their data
# dirs (YAML for bát-trạch, cung-mệnh, room rules, house templates) into the
# wheel. Hatchling resolves these paths during the editable install below,
# so the data directories MUST exist on disk at that point. Pre-stage them
# before the deps sync.
COPY packages/ontology/src/ontology/data packages/ontology/src/ontology/data
COPY packages/generator/src/generator/data packages/generator/src/generator/data

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --package phongthuy-api || \
    uv sync --no-install-project --package phongthuy-api

# Copy source
COPY apps/api/src apps/api/src
COPY packages/cv/src packages/cv/src
COPY packages/ontology/src packages/ontology/src
COPY packages/dataset/src packages/dataset/src
COPY packages/generator/src packages/generator/src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package phongthuy-api

EXPOSE 8000

CMD ["uv", "run", "--package", "phongthuy-api", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
