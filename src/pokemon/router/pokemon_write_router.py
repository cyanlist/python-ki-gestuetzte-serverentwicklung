"""Router with the endpoints for writing Pokémon (POST and PUT).

The endpoints are added later. The router is already part of the app, so that the
file `fastapi_app.py` does not have to change when they are added.
"""

from fastapi import APIRouter

__all__ = ["router"]

router = APIRouter(prefix="/pokemon", tags=["Write"])
