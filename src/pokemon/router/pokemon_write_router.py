"""Router with the endpoints for writing Pokémon (POST and PUT)."""

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)

from pokemon.model.pokemon_create_request_model import PokemonCreateRequestModel
from pokemon.model.pokemon_update_request_model import PokemonUpdateRequestModel
from pokemon.router.dependencies import get_write_service
from pokemon.service.pokemon_write_service import PokemonWriteService

__all__ = ["router"]

router = APIRouter(prefix="/pokemon", tags=["Write"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create(
    data: PokemonCreateRequestModel,
    request: Request,
    service: Annotated[PokemonWriteService, Depends(get_write_service)],
) -> Response:
    """Create a new Pokémon with its detail and moves.

    The response has no body. The client follows the header `Location` to read the
    created resource.

    :param data: Validated request body
    :param request: Used to build the header `Location`
    :param service: Injected service with the business logic
    :return: `201` with the header `Location`
    :raises ConflictError: if the number or the name already exists (the app turns it
        into `409`)
    """
    pokemon = service.create(data)
    location = str(request.url_for("get_by_id", pokemon_id=pokemon.id))
    return Response(status_code=status.HTTP_201_CREATED, headers={"Location": location})


def _etag(version: int) -> str:
    """Build the value of the header ETag. The double quotes are part of the value."""
    return f'"{version}"'


def _parse_if_match(if_match: str | None) -> int:
    """Validate the header `If-Match` and extract the version from it.

    :param if_match: Value of the header `If-Match`, or None if it is missing
    :return: The version from the header
    :raises HTTPException: `428` if the header is missing, `412` if it is malformed
    """
    if if_match is None:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="The header If-Match is required",
        )
    if len(if_match) < 3 or not (if_match.startswith('"') and if_match.endswith('"')):
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail='The header If-Match must look like "3"',
        )
    try:
        return int(if_match[1:-1])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail='The header If-Match must look like "3"',
        ) from None


@router.put("/{pokemon_id}")
def update(
    pokemon_id: int,
    data: PokemonUpdateRequestModel,
    service: Annotated[PokemonWriteService, Depends(get_write_service)],
    if_match: Annotated[str | None, Header()] = None,
) -> Response:
    """Replace a Pokémon. The header `If-Match` with the version is required.

    :param pokemon_id: Pokédex number as path parameter
    :param data: Validated request body
    :param service: Injected service with the business logic
    :param if_match: Header with the version the client last read, e.g. `"3"`
    :return: `204` with the header `ETag`
    :raises NotFoundError: if no Pokémon has this number (the app turns it into `404`)
    :raises VersionOutdatedError: if the version is outdated (the app turns it into
        `412`)
    :raises ConflictError: if the new name belongs to another Pokémon (the app turns
        it into `409`)
    """
    version = _parse_if_match(if_match)
    pokemon = service.update(pokemon_id=pokemon_id, version=version, data=data)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": _etag(pokemon.version)},
    )
