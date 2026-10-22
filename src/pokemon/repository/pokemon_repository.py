"""Repository class with the queries for the entity class Pokemon."""

from typing import Final

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from pokemon.entity import Pokemon

__all__ = ["PokemonRepository"]


class PokemonRepository:
    """Repository class with the database queries for Pokémon."""

    def find_by_id(self, pokemon_id: int, session: Session) -> Pokemon | None:
        """Find a Pokémon by its Pokédex number.

        :param pokemon_id: Pokédex number of the wanted Pokémon
        :param session: Session of SQLAlchemy
        :return: The found Pokémon or None
        """
        statement: Final = (
            select(Pokemon)
            # JOIN for the 1:1 relation, one extra query for the 1:N relation
            .options(joinedload(Pokemon.detail), selectinload(Pokemon.moves))
            .where(Pokemon.id == pokemon_id)
        )
        return session.scalar(statement)

    def exists_by_id(self, pokemon_id: int, session: Session) -> bool:
        """Check whether a Pokémon with this number exists.

        :param pokemon_id: Pokédex number to check
        :param session: Session of SQLAlchemy
        :return: True, if a Pokémon with this number exists
        """
        statement: Final = (
            select(func.count()).select_from(Pokemon).where(Pokemon.id == pokemon_id)
        )
        return bool(session.scalar(statement))

    def exists_by_name(
        self, name: str, session: Session, *, exclude_id: int | None = None
    ) -> bool:
        """Check whether a Pokémon with this name exists.

        :param name: Name to check
        :param session: Session of SQLAlchemy
        :param exclude_id: Pokédex number to ignore. Needed for PUT, where a Pokémon
            may keep its own name.
        :return: True, if a Pokémon with this name exists
        """
        statement = (
            select(func.count()).select_from(Pokemon).where(Pokemon.name == name)
        )
        if exclude_id is not None:
            statement = statement.where(Pokemon.id != exclude_id)
        return bool(session.scalar(statement))

    def add(self, pokemon: Pokemon, session: Session) -> None:
        """Mark a new Pokémon (with its detail and moves) for INSERT.

        :param pokemon: New Pokémon to insert
        :param session: Session of SQLAlchemy
        """
        session.add(pokemon)
