"""Shared fixtures for the integration tests.

The tests use the real PostgreSQL container (`docker compose up -d` in
`extras/compose/postgres`). Before every test the tables are emptied and filled with
the seed data again, so every test starts with the same 12 Pokémon.

WARNING: the tests wipe the tables of the database that `app.toml` points to.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Final

import pytest
from fastapi.testclient import TestClient

from pokemon.fastapi_app import app
from pokemon.repository.session_factory import engine

# tests/integration/conftest.py -> parents[2] is the project root
SEED_FILE: Final = (
    Path(__file__).parents[2]
    / "extras"
    / "compose"
    / "postgres"
    / "init"
    / "02-seed.sql"
)


@pytest.fixture(autouse=True)
def reset_database() -> None:
    """Reload the seed data before every test."""
    seed_sql = SEED_FILE.read_text(encoding="utf-8")
    # A raw connection allows several SQL statements in one execute() call
    connection = engine.raw_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "TRUNCATE pokemon.move, pokemon.pokemon_detail, pokemon.pokemon "
            "RESTART IDENTITY CASCADE"
        )
        cursor.execute(seed_sql)
        cursor.close()
        connection.commit()
    finally:
        connection.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A client that calls the app in the same process, without starting a server."""
    with TestClient(app) as test_client:
        yield test_client
