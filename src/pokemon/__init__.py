"""Pokémon API."""

import uvicorn


def main() -> None:
    """Start the ASGI server. Entry point for `uv run pokemon`."""
    uvicorn.run("pokemon.fastapi_app:app", host="127.0.0.1", port=8000, reload=True)
