"""Entity classes. All of them are imported here, so that SQLAlchemy finds the
relations between them by name."""

from pokemon.entity.base import Base
from pokemon.entity.move import Move
from pokemon.entity.pokemon import Pokemon
from pokemon.entity.pokemon_detail import PokemonDetail

__all__ = ["Base", "Move", "Pokemon", "PokemonDetail"]
