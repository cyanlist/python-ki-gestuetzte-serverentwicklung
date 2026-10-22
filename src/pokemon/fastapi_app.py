"""FastAPI application."""

from fastapi import FastAPI

app = FastAPI(title="Pokémon API")


@app.get("/")
def root() -> dict[str, str]:
    """Return a greeting to check that the server runs."""
    return {"message": "Hello from pokemon!"}
