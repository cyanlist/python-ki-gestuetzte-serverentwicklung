"""Pydantic model for a move in the request body of POST."""

from pydantic import BaseModel, ConfigDict, Field

from pokemon.model.pokemon_type import PokemonType

__all__ = ["MoveCreateRequestModel"]


class MoveCreateRequestModel(BaseModel):
    """A move in the request body of POST."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=50)
    type: PokemonType
    power: int | None = Field(default=None, gt=0)
    """NULL for status moves."""

    accuracy: int | None = Field(default=None, ge=1, le=100)
