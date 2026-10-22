# syntax=docker/dockerfile:1

# Lightweight base: just Python, no OS build toolchain. Alpine is avoided because
# musl libc needs psycopg to be rebuilt from source; slim (Debian) keeps the
# prebuilt psycopg[binary] wheel usable.
FROM python:3.13-slim

# Official static uv binary, no separate installer or pip install needed.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# Install dependencies before copying the source, so this layer is cached as
# long as pyproject.toml and uv.lock stay unchanged.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY src ./src
COPY README.md ./
RUN uv sync --frozen --no-dev

EXPOSE 8000

# Calls uvicorn directly, not through `uv run` (which would re-sync the
# project at every container start, pulling the dev dependencies this image
# was built without) and not through the `pokemon` script's main() (which
# binds 127.0.0.1 and enables the file-watcher reload meant for local dev).
CMD ["uvicorn", "pokemon.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
