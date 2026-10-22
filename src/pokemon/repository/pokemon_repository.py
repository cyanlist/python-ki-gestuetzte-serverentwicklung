"""Repository class with the queries for the entity class Pokemon."""

from typing import Final

from sqlalchemy import select
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
