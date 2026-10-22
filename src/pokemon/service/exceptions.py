"""Exceptions of the business logic.

The business logic raises them. The app turns them into HTTP status codes (see the
exception handlers in `fastapi_app.py`).
"""

__all__ = ["ConflictError", "NotFoundError", "VersionOutdatedError"]


class NotFoundError(Exception):
    """Exception, if no Pokémon exists for the requested Pokédex number."""

    def __init__(self, pokemon_id: int) -> None:
        """Remember the Pokédex number that was not found.

        :param pokemon_id: Pokédex number without a Pokémon
        """
        super().__init__(f"No Pokémon with the number {pokemon_id}")
        self.pokemon_id = pokemon_id


class ConflictError(Exception):
    """Exception, if the data conflicts with existing data, e.g. a duplicate name."""

    def __init__(self, message: str) -> None:
        """Remember the reason of the conflict.

        :param message: Description of the conflict
        """
        super().__init__(message)


class VersionOutdatedError(Exception):
    """Exception, if the client works with an outdated version of a Pokémon."""

    def __init__(self, version: int) -> None:
        """Remember the version that the client sent.

        :param version: Outdated version number
        """
        super().__init__(f"The version {version} is outdated")
        self.version = version
