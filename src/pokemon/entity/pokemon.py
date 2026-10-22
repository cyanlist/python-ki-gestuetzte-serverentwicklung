"""Entity class for a Pokémon. It is the main table."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pokemon.entity.base import Base

if TYPE_CHECKING:
    from pokemon.entity.move import Move
    from pokemon.entity.pokemon_detail import PokemonDetail

__all__ = ["Pokemon"]


class Pokemon(Base):
    """Entity class for a Pokémon."""

    __tablename__ = "pokemon"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    """The Pokédex number. It is set by the caller and not generated."""

    name: Mapped[str]
    type_1: Mapped[str]
    type_2: Mapped[str | None]
    height_m: Mapped[float] = mapped_column(Numeric(4, 1, asdecimal=False))
    weight_kg: Mapped[float] = mapped_column(Numeric(5, 1, asdecimal=False))
    legendary: Mapped[bool]

    version: Mapped[int] = mapped_column()
    """Version number for optimistic locking."""

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    """Timestamp of the last change. The database sets it on INSERT."""

    detail: Mapped["PokemonDetail | None"] = relationship(
        back_populates="pokemon",
        cascade="all, delete-orphan",
    )
    """The 1:1 relation: at most one detail row per Pokémon."""

    moves: Mapped[list["Move"]] = relationship(
        back_populates="pokemon",
        cascade="all, delete-orphan",
    )
    """The 1:N relation: many moves per Pokémon."""

    # SQLAlchemy raises StaleDataError if the row was changed by someone else
    __mapper_args__ = {"version_id_col": version}

    def __repr__(self) -> str:
        """Short representation without the relations (they would trigger queries)."""
        return f"Pokemon(id={self.id}, name={self.name!r}, version={self.version})"
