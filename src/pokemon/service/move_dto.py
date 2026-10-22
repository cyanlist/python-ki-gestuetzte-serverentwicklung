"""DTO class for a move, without any decorators of SQLAlchemy."""

from dataclasses import dataclass
from typing import Self

from pokemon.entity import Move

__all__ = ["MoveDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
class MoveDTO:
    """DTO class for a move."""

    name: str
    type: str
    power: int | None
    accuracy: int | None

    @classmethod
    def from_move(cls, move: Move) -> Self:
        """Create the DTO from an entity object.

        :param move: Entity object of SQLAlchemy
        :return: DTO with the data of the entity object
        """
        return cls(
            name=move.name,
            type=move.type,
            power=move.power,
            accuracy=move.accuracy,
        )
