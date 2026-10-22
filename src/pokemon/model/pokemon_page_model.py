"""Pydantic model for one page of Pokémon search results."""

from pydantic import BaseModel

from pokemon.model.page_info_model import PageInfoModel
from pokemon.model.pokemon_response_model import PokemonResponseModel

__all__ = ["PokemonPageModel"]


class PokemonPageModel(BaseModel):
    """One page of search results."""

    content: list[PokemonResponseModel]
    page: PageInfoModel
