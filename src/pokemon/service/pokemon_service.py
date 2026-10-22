"""Business logic for reading Pokémon."""

from typing import Final

from pokemon.repository.pokemon_repository import PokemonRepository
from pokemon.repository.session_factory import SessionFactory
from pokemon.service.exceptions import NotFoundError
from pokemon.service.pokemon_dto import PokemonDTO

__all__ = ["PokemonService"]


class PokemonService:
    """Service class with the business logic for reading Pokémon."""

    def __init__(self, repo: PokemonRepository) -> None:
        """Use the given repository for the database access."""
        self.repo: Final = repo

    def find_by_id(self, pokemon_id: int) -> PokemonDTO:
        """Find a Pokémon by its Pokédex number.

        :param pokemon_id: Pokédex number of the wanted Pokémon
        :return: The found Pokémon
        :raises NotFoundError: if no Pokémon has this number
        """
        # "with" closes the session at the end of the block
        with SessionFactory() as session:
            pokemon = self.repo.find_by_id(pokemon_id=pokemon_id, session=session)
            if pokemon is None:
                raise NotFoundError(pokemon_id)
            # The DTO is created inside the block, while the session is still open
            return PokemonDTO.from_pokemon(pokemon)
