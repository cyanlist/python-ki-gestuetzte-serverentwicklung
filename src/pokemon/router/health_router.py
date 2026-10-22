"""Health checks: is the app alive, and is it ready to handle requests?"""

from fastapi import APIRouter, Request, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from pokemon.model.health_status_model import HealthStatusModel
from pokemon.repository.session_factory import engine

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
def live() -> HealthStatusModel:
    """Liveness: the process is up and answers requests.

    It has no dependencies on purpose. If this endpoint does not answer, the process
    is dead or hanging and has to be restarted.
    """
    return HealthStatusModel(status="live")


def _database_is_up() -> bool:
    """Check that the database answers a trivial query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    return True


@router.get(
    "/ready",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": HealthStatusModel,
            "description": "The app is up, but cannot handle requests (yet).",
        }
    },
)
def ready(request: Request, response: Response) -> HealthStatusModel:
    """Readiness: the app can handle requests, including a working database.

    The answer is `200` with `ready`, or `503` with `not_ready` while the app is
    starting or shutting down, or while the database is unreachable.
    """
    if request.app.state.ready and _database_is_up():
        return HealthStatusModel(status="ready")
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthStatusModel(status="not_ready")
