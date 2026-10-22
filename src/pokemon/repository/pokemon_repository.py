"""Repository class with the queries for the entity class Pokemon."""

from typing import Final

from sqlalchemy import func, or_, select
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

    def find(
        self,
        session: Session,
        *,
        name: str | None,
        type_: str | None,
        legendary: bool | None,
        page: int,
        size: int,
    ) -> tuple[list[Pokemon], int]:
        """Search Pokémon. Return one page and the total number of matches.

        :param session: Session of SQLAlchemy
        :param name: Part of the name, case-insensitive, or None for no filter
        :param type_: Matches `type_1` or `type_2`, or None for no filter
        :param legendary: Filter by the legendary flag, or None for no filter
        :param page: Page number, starting at 0
        :param size: Number of Pokémon per page
        :return: The Pokémon of the page and the total number of matches
        """
        conditions = []
        if name is not None:
            # autoescape: a "%" or "_" typed by the user is not a wildcard
            conditions.append(Pokemon.name.icontains(name, autoescape=True))
        if type_ is not None:
            conditions.append(or_(Pokemon.type_1 == type_, Pokemon.type_2 == type_))
        if legendary is not None:
            conditions.append(Pokemon.legendary == legendary)

        total = session.scalar(
            select(func.count()).select_from(Pokemon).where(*conditions)
        )
        statement = (
            select(Pokemon)
            .where(*conditions)
            .options(joinedload(Pokemon.detail), selectinload(Pokemon.moves))
            .order_by(Pokemon.id)
            .limit(size)
            .offset(page * size)
        )
        return list(session.scalars(statement).all()), total or 0
