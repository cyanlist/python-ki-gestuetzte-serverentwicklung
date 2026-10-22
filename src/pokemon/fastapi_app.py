"""FastAPI application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from pokemon.router.health_router import router as health_router
from pokemon.router.pokemon_router import router as pokemon_router
from pokemon.router.pokemon_write_router import router as pokemon_write_router
from pokemon.service.exceptions import (
    ConflictError,
    NotFoundError,
    VersionOutdatedError,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Mark the app as ready after the startup and as not ready on shutdown."""
    app.state.ready = True
    yield
    app.state.ready = False


app = FastAPI(title="Pokémon API", lifespan=lifespan)
app.state.ready = False  # becomes True when the startup has finished
app.include_router(health_router)
app.include_router(pokemon_router)
app.include_router(pokemon_write_router)


@app.get("/")
def root() -> dict[str, str]:
    """Return a greeting to check that the server runs."""
    return {"message": "Hello from pokemon!"}


# --------------------------------------------------------------------------------------
# Exception handlers: turn the exceptions of the business logic into status codes
# --------------------------------------------------------------------------------------
@app.exception_handler(NotFoundError)
def not_found_error_handler(_request: Request, error: NotFoundError) -> JSONResponse:
    """Turn a NotFoundError into the status code 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(error)},
    )


@app.exception_handler(ConflictError)
def conflict_error_handler(_request: Request, error: ConflictError) -> JSONResponse:
    """Turn a ConflictError into the status code 409."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(error)},
    )


@app.exception_handler(VersionOutdatedError)
def version_outdated_error_handler(
    _request: Request, error: VersionOutdatedError
) -> JSONResponse:
    """Turn a VersionOutdatedError into the status code 412."""
    return JSONResponse(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        content={"detail": str(error)},
    )
