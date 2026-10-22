"""Pydantic model for a Pokémon in a response."""

from typing import Self

from pydantic import BaseModel, ConfigDict

from pokemon.model.move_response_model import MoveResponseModel
from pokemon.model.pokemon_detail_response_model import PokemonDetailResponseModel
from pokemon.service.pokemon_dto import PokemonDTO

__all__ = ["PokemonResponseModel"]


class PokemonResponseModel(BaseModel):
    """Model of a found Pokémon.

    FastAPI converts the fields into JSON. `from_attributes=True` is needed, so that
    the nested objects (detail, moves) are taken from the attributes of the DTOs.
    The version is not part of the response. It is sent in the header `ETag`.
    """

    id: int
    name: str
    type_1: str
    type_2: str | None
    height_m: float
    weight_kg: float
    legendary: bool
    detail: PokemonDetailResponseModel | None
    moves: list[MoveResponseModel]

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")

    @classmethod
    def from_dto(cls, pokemon: PokemonDTO) -> Self:
        """Convert a PokemonDTO into the model of a response.

        :param pokemon: DTO of the service
        :return: Model for the response
        """
        return cls.model_validate(pokemon)
