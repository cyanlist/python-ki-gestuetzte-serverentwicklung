"""Router with the endpoints for reading Pokémon."""

from typing import Annotated

from fastapi import APIRouter, Depends

from pokemon.model.pokemon_response_model import PokemonResponseModel
from pokemon.router.dependencies import get_service
from pokemon.service.pokemon_service import PokemonService

__all__ = ["router"]

router = APIRouter(prefix="/pokemon", tags=["Read"])


@router.get("/{pokemon_id}", response_model=PokemonResponseModel)
def get_by_id(
    pokemon_id: int,
    service: Annotated[PokemonService, Depends(get_service)],
) -> PokemonResponseModel:
    """Find a Pokémon by its Pokédex number.

    :param pokemon_id: Pokédex number as path parameter
    :param service: Injected service with the business logic
    :return: The found Pokémon
    :raises NotFoundError: if no Pokémon has this number (the app turns it into 404)
    """
    pokemon = service.find_by_id(pokemon_id=pokemon_id)
    return PokemonResponseModel.from_dto(pokemon)
