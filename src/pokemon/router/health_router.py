"""Health checks: is the app alive, and is it ready to handle requests?"""

from fastapi import APIRouter, Request, Response, status

from pokemon.model.health_status_model import HealthStatusModel

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
def live() -> HealthStatusModel:
    """Liveness: the process is up and answers requests.

    It has no dependencies on purpose. If this endpoint does not answer, the process
    is dead or hanging and has to be restarted.
    """
    return HealthStatusModel(status="live")


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
    """Readiness: the app can handle requests.

    The answer is `200` with `ready`, or `503` with `not_ready` while the app is
    starting or shutting down. Add checks of other dependencies here later, for
    example a query `SELECT 1` against the database.
    """
    if request.app.state.ready:
        return HealthStatusModel(status="ready")
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthStatusModel(status="not_ready")
