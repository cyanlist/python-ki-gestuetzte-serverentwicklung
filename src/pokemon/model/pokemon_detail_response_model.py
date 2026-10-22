"""Pydantic model for the details of a Pokémon in a response."""

from pydantic import BaseModel, ConfigDict

__all__ = ["PokemonDetailResponseModel"]


class PokemonDetailResponseModel(BaseModel):
    """The details of a Pokémon as part of a response."""

    catch_rate: int
    base_experience: int

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")
