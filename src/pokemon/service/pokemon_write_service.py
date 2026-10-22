"""Business logic for writing Pokémon.

This class is the place for the write operations (create and update). Like the
professor's `PatientWriteService`, it is separated from the read service, so that two
people can work on reading and writing without touching the same files.
"""

from typing import Final

from pokemon.repository.pokemon_repository import PokemonRepository

__all__ = ["PokemonWriteService"]


class PokemonWriteService:
    """Service class with the business logic for writing Pokémon."""

    def __init__(self, repo: PokemonRepository) -> None:
        """Use the given repository for the database access."""
        self.repo: Final = repo
