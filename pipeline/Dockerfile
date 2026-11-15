# syntax=docker/dockerfile:1
# EV Finder jobs image (T-013, Decisions 005, 006, 007). Entrypoint: the `ev` CLI.
# Build context = repo root (the pipeline reads packages/schema/schemas at runtime):
#   docker buildx build --platform linux/arm64 -f pipeline/Dockerfile -t ev-finder-jobs .
# Data lives outside the image: mount it and point EV_DATA_DIR at it (default /data).

ARG PYTHON_VERSION=3.12

# uv binary from the official image, pinned to the version the lockfile was made with
# (uv 0.11.32 locally, 2026-11-15) so builds are reproducible. Bump together with uv.lock.
ARG UV_VERSION=0.11.32
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM python:${PYTHON_VERSION}-slim AS runtime
COPY --from=uv /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/pipeline/.venv \
    EV_DATA_DIR=/data \
    PATH=/app/pipeline/.venv/bin:$PATH

WORKDIR /app/pipeline

# Dependencies first (cached layer), then the project itself.
COPY pipeline/pyproject.toml pipeline/uv.lock ./
# Optional secret `extra_ca`: a CA bundle for builds behind a TLS-intercepting proxy
# (`--secret id=extra_ca,src=ca.crt`). Not needed in CI; never stored in a layer.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=secret,id=extra_ca,required=false \
    if [ -f /run/secrets/extra_ca ]; then export SSL_CERT_FILE=/run/secrets/extra_ca; fi; \
    uv sync --frozen --no-dev --no-install-project

COPY packages/schema/schemas /app/packages/schema/schemas
COPY pipeline/ ./
# Same optional `extra_ca` secret as above: this step fetches the build backend (hatchling).
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=secret,id=extra_ca,required=false \
    if [ -f /run/secrets/extra_ca ]; then export SSL_CERT_FILE=/run/secrets/extra_ca; fi; \
    uv sync --frozen --no-dev

# Non-root user; code stays root-owned and read-only, /data is the only writable path.
RUN useradd --system --uid 10001 --home-dir /nonexistent --shell /usr/sbin/nologin ev \
 && mkdir -p /data && chown ev:ev /data
USER ev

ENTRYPOINT ["ev"]
CMD ["--help"]
