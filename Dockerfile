FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd -g ${USER_GID} appgroup && \
    useradd -u ${USER_UID} -g appgroup -m appuser

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY --chown=appuser:appgroup . .

RUN uv sync --frozen 
    
USER appuser
