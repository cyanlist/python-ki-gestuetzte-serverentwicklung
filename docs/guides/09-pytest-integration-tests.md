# 09 pytest integration tests

**Goal:** Automatic tests that call the app and check GET, POST (and PUT). One command,
`uv run pytest`, runs them all.

**Checklist items:** Testing → GET requests tested, POST requests tested, tests can be
repeated.

> The course accepts **one** way of testing: pytest **or** an API client such as
> Postman or Bruno (guide 10). Pick at least one.

## Background

- **Integration test:** the test uses the real parts together (router, service,
  repository and the PostgreSQL container). That is exactly what the checklist asks
  for. A unit test would replace the database with a fake. That is not needed here.
- **`TestClient`** from FastAPI calls the app **in the same process**, without a
  network port. You do not start the server for the tests, but the database
  container must run.
- **Repeatable tests:** the tests change data (POST, PUT). A fixture therefore
  empties the tables and loads the seed data again **before every test**. Every test
  starts with the same 12 Pokémon, and the order of the tests does not matter.
- **Fixture:** a function with `@pytest.fixture` that prepares something. A test gets
  it by naming it as a parameter (`client`). With `autouse=True` it runs for every test.
- **Arrange, act, assert:** each test prepares the data, calls the endpoint once and
  checks the result.

> **Warning:** the tests **wipe the tables** of the database that `.env` points to.
> That is fine for this project because the seed data is loaded again, but do not point
> `.env` at a database with data you want to keep. A cleaner setup would use a second
> database for the tests (see "Going further").

## Steps

### 1. Install the test client

```shell
uv add --dev httpx2
```

`pytest` is already installed. FastAPI's `TestClient` needs an HTTP client library.
Recent Starlette versions ask for `httpx2` and print a deprecation warning when the
older `httpx` is used.

### 2. Configure pytest in `pyproject.toml`

Add at the end:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 3. Fixtures: `tests/conftest.py`

`conftest.py` is a special file: pytest finds the fixtures in it automatically.

```python
"""Shared fixtures for the integration tests.

The tests use the real PostgreSQL container (see the README). Before every test the
tables are emptied and filled with the seed data again, so every test starts with
the same 12 Pokémon.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pokemon.app import app
from pokemon.database import engine

SEED_FILE = (
    Path(__file__).parents[1]
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
            "TRUNCATE pokemon.attacke, pokemon.pokemon_detail, pokemon.pokemon "
            "RESTART IDENTITY CASCADE"
        )
        cursor.execute(seed_sql)
        cursor.close()
        connection.commit()
    finally:
        connection.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A client that calls the app in-process, without starting a server."""
    with TestClient(app) as test_client:
        yield test_client
```

The seed file is the same file the container uses, so there is **one** source for the
test data.

### 4. GET tests: `tests/test_get.py`

```python
"""Integration tests for the GET requests."""

from fastapi.testclient import TestClient


def test_get_by_id(client: TestClient) -> None:
    response = client.get("/pokemon/644")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Zekrom"
    assert body["typ1"] == "Drache"
    assert body["detail"]["fangrate"] == 3
    assert {attacke["name"] for attacke in body["attacken"]} == {
        "Donnerblitz",
        "Drachenklaue",
    }


def test_get_by_id_not_found(client: TestClient) -> None:
    response = client.get("/pokemon/999999")

    assert response.status_code == 404


def test_get_by_id_invalid_id(client: TestClient) -> None:
    response = client.get("/pokemon/abc")

    assert response.status_code == 422


def test_get_by_id_returns_etag(client: TestClient) -> None:
    response = client.get("/pokemon/644")

    assert response.headers["ETag"] == '"0"'


def test_get_by_id_conditional_not_modified(client: TestClient) -> None:
    etag = client.get("/pokemon/644").headers["ETag"]

    response = client.get("/pokemon/644", headers={"If-None-Match": etag})

    assert response.status_code == 304
    assert response.content == b""


def test_get_by_id_conditional_outdated_etag(client: TestClient) -> None:
    response = client.get("/pokemon/644", headers={"If-None-Match": '"99"'})

    assert response.status_code == 200


def test_get_all_first_page(client: TestClient) -> None:
    response = client.get("/pokemon")

    assert response.status_code == 200
    body = response.json()
    assert len(body["content"]) == 10
    assert body["page"] == {
        "size": 10,
        "number": 0,
        "total_elements": 12,
        "total_pages": 2,
    }


def test_get_by_typ(client: TestClient) -> None:
    response = client.get("/pokemon", params={"typ": "Feuer"})

    names = {pokemon["name"] for pokemon in response.json()["content"]}
    assert names == {"Victini", "Floink", "Skelabra", "Reshiram"}


def test_get_by_name_part(client: TestClient) -> None:
    response = client.get("/pokemon", params={"name": "zo"})

    names = {pokemon["name"] for pokemon in response.json()["content"]}
    assert names == {"Zorua", "Zoroark"}


def test_get_legendary_second_page(client: TestClient) -> None:
    response = client.get("/pokemon", params={"legendaer": True, "size": 2, "page": 1})

    names = [pokemon["name"] for pokemon in response.json()["content"]]
    assert names == ["Zekrom", "Kyurem"]


def test_get_without_result(client: TestClient) -> None:
    response = client.get("/pokemon", params={"name": "does-not-exist"})

    assert response.status_code == 200
    assert response.json()["content"] == []


def test_get_with_unknown_parameter(client: TestClient) -> None:
    response = client.get("/pokemon", params={"foo": "bar"})

    assert response.status_code == 422
```

### 5. POST tests: `tests/test_post.py`

```python
"""Integration tests for the POST request."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

NEW_POKEMON: dict[str, Any] = {
    "id": 600,
    "name": "Testmon",
    "typ1": "Feuer",
    "typ2": None,
    "groesse_m": 1.2,
    "gewicht_kg": 30.5,
    "legendaer": False,
    "detail": {"fangrate": 100, "basis_erfahrung": 150},
    "attacken": [{"name": "Glut", "typ": "Feuer", "staerke": 40, "genauigkeit": 100}],
}


def test_post(client: TestClient) -> None:
    response = client.post("/pokemon", json=NEW_POKEMON)

    assert response.status_code == 201
    location = response.headers["Location"]
    assert location.endswith("/pokemon/600")

    created = client.get(location).json()
    assert created["name"] == "Testmon"
    assert created["detail"]["fangrate"] == 100
    assert created["attacken"][0]["name"] == "Glut"


def test_post_existing_id(client: TestClient) -> None:
    response = client.post("/pokemon", json={**NEW_POKEMON, "id": 644})

    assert response.status_code == 409


def test_post_existing_name(client: TestClient) -> None:
    response = client.post("/pokemon", json={**NEW_POKEMON, "name": "Zekrom"})

    assert response.status_code == 409


@pytest.mark.parametrize(
    "changes",
    [
        {"id": 100},
        {"name": ""},
        {"typ1": "Quatsch"},
        {"groesse_m": -1},
        {"detail": {"fangrate": 0, "basis_erfahrung": 1}},
        {"detail": None},
        {"unknown_field": 1},
    ],
)
def test_post_invalid_data(client: TestClient, changes: dict[str, Any]) -> None:
    response = client.post("/pokemon", json={**NEW_POKEMON, **changes})

    assert response.status_code == 422


def test_post_broken_json(client: TestClient) -> None:
    response = client.post(
        "/pokemon",
        content="{broken",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
```

`@pytest.mark.parametrize` runs the same test once per entry. That is seven tests for
seven kinds of invalid data, with no copied code.

### 6. PUT tests: `tests/test_put.py`

```python
"""Integration tests for the PUT request."""

from typing import Any

from fastapi.testclient import TestClient

ZEKROM: dict[str, Any] = {
    "name": "Zekrom",
    "typ1": "Drache",
    "typ2": "Elektro",
    "groesse_m": 3.0,
    "gewicht_kg": 345.0,
    "legendaer": True,
}


def test_put(client: TestClient) -> None:
    etag = client.get("/pokemon/644").headers["ETag"]

    response = client.put("/pokemon/644", json=ZEKROM, headers={"If-Match": etag})

    assert response.status_code == 204
    assert response.headers["ETag"] == '"1"'
    assert client.get("/pokemon/644").json()["groesse_m"] == 3.0


def test_put_without_if_match(client: TestClient) -> None:
    response = client.put("/pokemon/644", json=ZEKROM)

    assert response.status_code == 428


def test_put_malformed_if_match(client: TestClient) -> None:
    response = client.put("/pokemon/644", json=ZEKROM, headers={"If-Match": "abc"})

    assert response.status_code == 412


def test_put_outdated_version(client: TestClient) -> None:
    headers = {"If-Match": '"0"'}
    assert client.put("/pokemon/644", json=ZEKROM, headers=headers).status_code == 204

    # The same request again uses the version that is outdated now: lost update
    response = client.put("/pokemon/644", json=ZEKROM, headers=headers)

    assert response.status_code == 412


def test_put_not_found(client: TestClient) -> None:
    response = client.put("/pokemon/999999", json=ZEKROM, headers={"If-Match": '"0"'})

    assert response.status_code == 404


def test_put_existing_name(client: TestClient) -> None:
    response = client.put(
        "/pokemon/644",
        json={**ZEKROM, "name": "Reshiram"},
        headers={"If-Match": '"0"'},
    )

    assert response.status_code == 409


def test_put_invalid_data(client: TestClient) -> None:
    response = client.put(
        "/pokemon/644",
        json={**ZEKROM, "groesse_m": -1},
        headers={"If-Match": '"0"'},
    )

    assert response.status_code == 422
```

## Check it

Start the database (`docker compose up -d` in `extras/compose/postgres`), then:

```shell
uv run pytest
```

Expected: `30 passed`. More ways to run:

```shell
uv run pytest -v                      # one line per test
uv run pytest tests/test_get.py       # one file
uv run pytest -k conditional          # tests with "conditional" in the name
uv run pytest -x                      # stop at the first failure
uv run pytest --lf                    # only the tests that failed last time
```

Then:

```shell
uv run ruff format
uv run ruff check
uv run ty check
```

## Common pitfalls

| Problem | Cause and fix |
|---|---|
| `connection refused` or `OperationalError` | The container does not run. |
| `FileNotFoundError: ... 02-seed.sql` | The path in `SEED_FILE` is wrong. `parents[1]` of `tests/conftest.py` is the project root. |
| `ModuleNotFoundError: pokemon` | Run `uv run pytest` from the project root, not `pytest` without `uv run`. |
| Tests fail only when run together | A test depends on data of another test. The fixture resets the data, so check that `autouse=True` is set. |
| `422` in a test that should pass | Print `response.json()`. It names the field. |
| `ValidationError: db_password` | `.env` is missing in the folder you run `pytest` from. |
| A test passes alone but a count is wrong | Someone added data by hand and the reset did not run. Run the test again. |
| Warning about `httpx` and `starlette.testclient` | Install `httpx2` (step 1) and remove `httpx`. |

## Going further (optional)

- **Separate test database:** create a second database, for example `pokemon_test`
  (`CREATE DATABASE pokemon_test;`), run `01-schema.sql` in it, and start the tests with
  `DB_NAME=pokemon_test`. Then the tests never touch your development data.
- **Test the service without a database** with a fake repository. This is what the
  dependency injection allows (`app.dependency_overrides`).
- **Coverage:** `uv add --dev pytest-cov` and `uv run pytest --cov=pokemon`.

## Commit

```shell
git add pyproject.toml uv.lock tests
git commit -m "test: add integration tests for GET, POST and PUT"
```

If you want small commits, commit the files one by one: `test: add GET tests`,
`test: add POST tests`, `test: add PUT tests`.

## Prompt idea

```text
Context: FastAPI project (src/pokemon), PostgreSQL in Docker, seed data in
extras/compose/postgres/init/02-seed.sql. pytest and httpx2 are installed.
Task: Write integration tests with FastAPI's TestClient. tests/conftest.py has an
autouse fixture that truncates the three tables and reloads 02-seed.sql before every
test, and a client fixture. Write tests for GET by id (200, 404, 422, ETag, 304),
GET with query parameters (type, name, legendary, paging, no result, unknown
parameter), POST (201 with Location, 409 for duplicates, parametrized 422 cases) and
PUT (204, 428, 412, 404, 409, 422). Type hints, English names and comments.
```
