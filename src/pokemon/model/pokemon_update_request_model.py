"""Pydantic model for the request body of PUT."""

from pokemon.model.pokemon_base_request_model import PokemonBaseRequestModel

__all__ = ["PokemonUpdateRequestModel"]


class PokemonUpdateRequestModel(PokemonBaseRequestModel):
    """Request body of PUT: all fields of the Pokémon itself.

    PUT replaces the whole resource, so no field is optional (except `type_2`).
    Detail and moves are not changed by PUT.
    """
