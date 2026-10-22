"""FastAPI application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from pokemon.router.health_router import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Mark the app as ready after the startup and as not ready on shutdown."""
    app.state.ready = True
    yield
    app.state.ready = False


app = FastAPI(title="Pokémon API", lifespan=lifespan)
app.state.ready = False  # becomes True when the startup has finished
app.include_router(health_router)


@app.get("/")
def root() -> dict[str, str]:
    """Return a greeting to check that the server runs."""
    return {"message": "Hello from pokemon!"}
