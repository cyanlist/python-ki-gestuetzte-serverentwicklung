"""Pydantic model for the details in the request body of POST."""

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["PokemonDetailCreateRequestModel"]


class PokemonDetailCreateRequestModel(BaseModel):
    """The details in the request body of POST."""

    model_config = ConfigDict(extra="forbid")

    catch_rate: int = Field(ge=1, le=255)
    base_experience: int = Field(gt=0)
