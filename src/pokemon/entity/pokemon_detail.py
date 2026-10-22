"""Entity class for the details of a Pokémon (1:1)."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pokemon.entity.base import Base

if TYPE_CHECKING:
    from pokemon.entity.pokemon import Pokemon

__all__ = ["PokemonDetail"]


class PokemonDetail(Base):
    """Entity class for the details of a Pokémon (1:1)."""

    __tablename__ = "pokemon_detail"

    id: Mapped[int] = mapped_column(primary_key=True)
    pokemon_id: Mapped[int] = mapped_column(
        ForeignKey("pokemon.pokemon.id"), unique=True
    )
    catch_rate: Mapped[int]
    base_experience: Mapped[int]

    pokemon: Mapped["Pokemon"] = relationship(back_populates="detail")
