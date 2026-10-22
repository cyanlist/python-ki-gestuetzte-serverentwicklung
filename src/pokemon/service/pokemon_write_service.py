"""Business logic for writing Pokémon.

This class is the place for the write operations (create and update). Like the
professor's `PatientWriteService`, it is separated from the read service, so that two
people can work on reading and writing without touching the same files.
"""

from typing import Final

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from pokemon.entity import Move, Pokemon, PokemonDetail
from pokemon.model.pokemon_create_request_model import PokemonCreateRequestModel
from pokemon.model.pokemon_update_request_model import PokemonUpdateRequestModel
from pokemon.repository.pokemon_repository import PokemonRepository
from pokemon.repository.session_factory import SessionFactory
from pokemon.service.exceptions import (
    ConflictError,
    NotFoundError,
    VersionOutdatedError,
)
from pokemon.service.pokemon_dto import PokemonDTO

__all__ = ["PokemonWriteService"]


class PokemonWriteService:
    """Service class with the business logic for writing Pokémon."""

    def __init__(self, repo: PokemonRepository) -> None:
        """Use the given repository for the database access."""
        self.repo: Final = repo

    def create(self, data: PokemonCreateRequestModel) -> PokemonDTO:
        """Create a new Pokémon with its detail and moves.

        :param data: Validated request body
        :return: The created Pokémon
        :raises ConflictError: if the number or the name already exists
        """
        with SessionFactory() as session:
            if self.repo.exists_by_id(pokemon_id=data.id, session=session):
                raise ConflictError(
                    f"A Pokémon with the number {data.id} already exists"
                )
            if self.repo.exists_by_name(name=data.name, session=session):
                raise ConflictError(
                    f"A Pokémon with the name {data.name} already exists"
                )

            pokemon = Pokemon(
                id=data.id,
                name=data.name,
                type_1=data.type_1.value,
                type_2=data.type_2.value if data.type_2 is not None else None,
                height_m=data.height_m,
                weight_kg=data.weight_kg,
                legendary=data.legendary,
                detail=PokemonDetail(
                    catch_rate=data.detail.catch_rate,
                    base_experience=data.detail.base_experience,
                ),
                moves=[
                    Move(
                        name=move.name,
                        type=move.type.value,
                        power=move.power,
                        accuracy=move.accuracy,
                    )
                    for move in data.moves
                ],
            )
            self.repo.add(pokemon=pokemon, session=session)
            try:
                session.commit()
            except IntegrityError as error:
                # Another request was faster than the checks above (race condition)
                session.rollback()
                raise ConflictError("The Pokémon already exists") from error
            # The DTO is created inside the block, while the session is still open
            return PokemonDTO.from_pokemon(pokemon)

    def update(
        self, pokemon_id: int, version: int, data: PokemonUpdateRequestModel
    ) -> PokemonDTO:
        """Replace the data of a Pokémon if the client knows the current version.

        :param pokemon_id: Pokédex number of the Pokémon
        :param version: Version the client last read
        :param data: Validated request body
        :return: The updated Pokémon
        :raises NotFoundError: if no Pokémon has this number
        :raises VersionOutdatedError: if the version is not the current one
        :raises ConflictError: if the new name belongs to another Pokémon
        """
        with SessionFactory() as session:
            pokemon = self.repo.find_by_id(pokemon_id=pokemon_id, session=session)
            if pokemon is None:
                raise NotFoundError(pokemon_id)
            if pokemon.version != version:
                raise VersionOutdatedError(version)
            if self.repo.exists_by_name(
                name=data.name, session=session, exclude_id=pokemon_id
            ):
                raise ConflictError(
                    f"A Pokémon with the name {data.name} already exists"
                )

            pokemon.name = data.name
            pokemon.type_1 = data.type_1.value
            pokemon.type_2 = data.type_2.value if data.type_2 is not None else None
            pokemon.height_m = data.height_m
            pokemon.weight_kg = data.weight_kg
            pokemon.legendary = data.legendary
            try:
                session.commit()
            except StaleDataError as error:
                # Someone changed the row between our check and the UPDATE
                session.rollback()
                raise VersionOutdatedError(version) from error
            except IntegrityError as error:
                session.rollback()
                raise ConflictError("The name already exists") from error
            return PokemonDTO.from_pokemon(pokemon)
