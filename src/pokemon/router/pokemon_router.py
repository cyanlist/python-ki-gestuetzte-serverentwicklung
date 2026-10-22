"""Router with the endpoints for reading Pokémon."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response, status

from pokemon.model.pokemon_response_model import PokemonResponseModel
from pokemon.router.constants import ETAG
from pokemon.router.dependencies import get_service
from pokemon.service.pokemon_service import PokemonService

__all__ = ["router"]

router = APIRouter(prefix="/pokemon", tags=["Read"])


def _etag(version: int) -> str:
    """Build the value of the header ETag. The double quotes are part of the value."""
    return f'"{version}"'


def _is_not_modified(if_none_match: str | None, etag: str) -> bool:
    """Check whether the client already has the current version of the resource.

    The header can contain a list of ETags (`"1", "2"`), weak ETags (`W/"1"`) or `*`.

    :param if_none_match: Value of the request header If-None-Match or None
    :param etag: ETag of the current version
    :return: True, if the client's copy is still up to date
    """
    if if_none_match is None:
        return False
    candidates = [
        value.strip().removeprefix("W/") for value in if_none_match.split(",")
    ]
    return etag in candidates or "*" in candidates


@router.get(
    "/{pokemon_id}",
    response_model=PokemonResponseModel,
    responses={
        status.HTTP_304_NOT_MODIFIED: {
            "description": "The version in If-None-Match is still current. No body.",
        },
    },
)
def get_by_id(
    pokemon_id: int,
    response: Response,
    service: Annotated[PokemonService, Depends(get_service)],
    if_none_match: Annotated[str | None, Header()] = None,
) -> PokemonResponseModel | Response:
    """Find a Pokémon by its Pokédex number (conditional GET).

    The response has the header `ETag` with the version of the Pokémon. If the request
    has the header `If-None-Match` with the current version, the answer is `304`
    without a body.

    :param pokemon_id: Pokédex number as path parameter
    :param response: Response object of FastAPI, used to set the header ETag
    :param service: Injected service with the business logic
    :param if_none_match: Optional header with the version that the client has
    :return: The found Pokémon, or an empty response with `304`
    :raises NotFoundError: if no Pokémon has this number (the app turns it into 404)
    """
    pokemon = service.find_by_id(pokemon_id=pokemon_id)
    etag = _etag(pokemon.version)

    if _is_not_modified(if_none_match, etag):
        return Response(
            status_code=status.HTTP_304_NOT_MODIFIED,
            headers={ETAG: etag},
        )

    response.headers[ETAG] = etag
    return PokemonResponseModel.from_dto(pokemon)
