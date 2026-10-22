"""Factory functions for dependency injection."""

from typing import Annotated

from fastapi import Depends

from pokemon.repository.pokemon_repository import PokemonRepository
from pokemon.service.pokemon_service import PokemonService
from pokemon.service.pokemon_write_service import PokemonWriteService

__all__ = ["get_repository", "get_service", "get_write_service"]


def get_repository() -> PokemonRepository:
    """Factory function for the PokemonRepository.

    :return: The repository
    """
    return PokemonRepository()


def get_service(
    repo: Annotated[PokemonRepository, Depends(get_repository)],
) -> PokemonService:
    """Factory function for the PokemonService (reading)."""
    return PokemonService(repo=repo)


def get_write_service(
    repo: Annotated[PokemonRepository, Depends(get_repository)],
) -> PokemonWriteService:
    """Factory function for the PokemonWriteService (creating and updating)."""
    return PokemonWriteService(repo=repo)
