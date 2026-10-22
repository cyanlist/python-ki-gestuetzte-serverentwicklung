"""DTO class for a Pokémon, without any decorators of SQLAlchemy."""

from dataclasses import dataclass
from typing import Self

from pokemon.entity import Pokemon
from pokemon.service.move_dto import MoveDTO
from pokemon.service.pokemon_detail_dto import PokemonDetailDTO

__all__ = ["PokemonDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
class PokemonDTO:
    """DTO class for a read or saved Pokémon.

    The session is closed when the service returns. A DTO has no connection to the
    database anymore, so nothing is loaded later by accident.
    """

    id: int
    version: int
    name: str
    type_1: str
    type_2: str | None
    height_m: float
    weight_kg: float
    legendary: bool
    detail: PokemonDetailDTO | None
    moves: list[MoveDTO]

    @classmethod
    def from_pokemon(cls, pokemon: Pokemon) -> Self:
        """Create the DTO from an entity object.

        :param pokemon: Entity object of SQLAlchemy
        :return: DTO with the data of the entity object
        """
        return cls(
            id=pokemon.id,
            version=pokemon.version,
            name=pokemon.name,
            type_1=pokemon.type_1,
            type_2=pokemon.type_2,
            height_m=pokemon.height_m,
            weight_kg=pokemon.weight_kg,
            legendary=pokemon.legendary,
            detail=(
                PokemonDetailDTO.from_pokemon_detail(pokemon.detail)
                if pokemon.detail is not None
                else None
            ),
            moves=[MoveDTO.from_move(move) for move in pokemon.moves],
        )
