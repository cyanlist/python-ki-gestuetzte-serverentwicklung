"""Pydantic model for the fields that POST and PUT have in common."""

from pydantic import BaseModel, ConfigDict, Field

from pokemon.model.pokemon_type import PokemonType

__all__ = ["PokemonBaseRequestModel"]


class PokemonBaseRequestModel(BaseModel):
    """Fields that POST and PUT have in common."""

    # extra="forbid": a typo in a field name leads to 422 instead of being ignored
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=50)
    type_1: PokemonType
    type_2: PokemonType | None = None
    height_m: float = Field(gt=0, le=999.9)
    """Matches the column `NUMERIC(4, 1)`."""

    weight_kg: float = Field(gt=0, le=9999.9)
    """Matches the column `NUMERIC(5, 1)`."""

    legendary: bool
