"""Pydantic model for a move in a response."""

from pydantic import BaseModel, ConfigDict

__all__ = ["MoveResponseModel"]


class MoveResponseModel(BaseModel):
    """A move of a Pokémon as part of a response."""

    name: str
    type: str
    power: int | None
    accuracy: int | None

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")
