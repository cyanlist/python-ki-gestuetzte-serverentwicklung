"""Pydantic model for the request body of POST."""

from pydantic import Field

from pokemon.model.move_create_request_model import MoveCreateRequestModel
from pokemon.model.pokemon_base_request_model import PokemonBaseRequestModel
from pokemon.model.pokemon_detail_create_request_model import (
    PokemonDetailCreateRequestModel,
)

__all__ = ["PokemonCreateRequestModel"]


class PokemonCreateRequestModel(PokemonBaseRequestModel):
    """Request body of POST: a new Pokémon with its detail and moves."""

    id: int = Field(ge=494, le=649)
    """The Pokédex number. Generation 5 covers the numbers 494 to 649."""

    detail: PokemonDetailCreateRequestModel
    moves: list[MoveCreateRequestModel] = Field(default_factory=list, max_length=4)
