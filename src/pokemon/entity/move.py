"""Entity class for a move of a Pokémon (1:N)."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pokemon.entity.base import Base

if TYPE_CHECKING:
    from pokemon.entity.pokemon import Pokemon

__all__ = ["Move"]


class Move(Base):
    """Entity class for a move of a Pokémon (1:N from the point of the Pokémon)."""

    __tablename__ = "move"

    id: Mapped[int] = mapped_column(primary_key=True)
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemon.pokemon.id"))
    name: Mapped[str]
    type: Mapped[str]
    power: Mapped[int | None]
    accuracy: Mapped[int | None]

    pokemon: Mapped["Pokemon"] = relationship(back_populates="moves")
