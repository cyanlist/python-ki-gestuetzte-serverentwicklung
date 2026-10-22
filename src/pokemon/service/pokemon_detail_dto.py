"""DTO class for the details of a Pokémon, without any decorators of SQLAlchemy."""

from dataclasses import dataclass
from typing import Self

from pokemon.entity import PokemonDetail

__all__ = ["PokemonDetailDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
class PokemonDetailDTO:
    """DTO class for the details of a Pokémon."""

    catch_rate: int
    base_experience: int

    @classmethod
    def from_pokemon_detail(cls, detail: PokemonDetail) -> Self:
        """Create the DTO from an entity object.

        :param detail: Entity object of SQLAlchemy
        :return: DTO with the data of the entity object
        """
        return cls(
            catch_rate=detail.catch_rate,
            base_experience=detail.base_experience,
        )
