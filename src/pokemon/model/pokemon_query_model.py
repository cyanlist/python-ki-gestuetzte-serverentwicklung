"""Pydantic model for the query parameters of GET /pokemon."""

from pydantic import BaseModel, ConfigDict, Field

from pokemon.model.pokemon_type import PokemonType

__all__ = ["PokemonQueryModel"]


class PokemonQueryModel(BaseModel):
    """Search and paging parameters of `GET /pokemon`."""

    # unknown query parameters lead to 422 instead of being ignored silently
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=50)
    """Part of the name, case-insensitive."""

    type: PokemonType | None = None
    """Matches `type_1` or `type_2`."""

    legendary: bool | None = None

    page: int = Field(default=0, ge=0)
    """Page number, starting at 0."""

    size: int = Field(default=10, ge=1, le=100)
    """Number of Pokémon per page."""
