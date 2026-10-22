"""Integration tests for the conditional GET `GET /pokemon/{pokemon_id}`.

The ETag is the version of the Pokémon in double quotes, e.g. `"0"`.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from pokemon.repository.session_factory import engine


def _bump_version(pokemon_id: int) -> None:
    """Simulate a change of the Pokémon by another client: the version grows."""
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE pokemon.pokemon SET version = version + 1 WHERE id = :id"),
            {"id": pokemon_id},
        )


def test_get_by_id_sends_etag(client: TestClient) -> None:
    response = client.get("/pokemon/644")

    assert response.status_code == 200
    assert response.headers["ETag"] == '"0"'


def test_get_by_id_if_none_match_with_current_version_returns_304(
    client: TestClient,
) -> None:
    etag = client.get("/pokemon/644").headers["ETag"]

    response = client.get("/pokemon/644", headers={"If-None-Match": etag})

    assert response.status_code == 304
    assert response.content == b""
    assert response.headers["ETag"] == etag


def test_get_by_id_if_none_match_with_other_version_returns_200(
    client: TestClient,
) -> None:
    response = client.get("/pokemon/644", headers={"If-None-Match": '"99"'})

    assert response.status_code == 200
    assert response.headers["ETag"] == '"0"'
    assert response.json()["name"] == "Zekrom"


@pytest.mark.parametrize(
    "if_none_match",
    ['W/"0"', '"7", "0"', "*"],
    ids=["weak etag", "list of etags", "star"],
)
def test_get_by_id_if_none_match_variants_return_304(
    client: TestClient, if_none_match: str
) -> None:
    response = client.get("/pokemon/644", headers={"If-None-Match": if_none_match})

    assert response.status_code == 304


@pytest.mark.parametrize("if_none_match", ["0", '""', "abc"])
def test_get_by_id_malformed_if_none_match_returns_200(
    client: TestClient, if_none_match: str
) -> None:
    # Without the double quotes the value is not an ETag, so it never matches
    response = client.get("/pokemon/644", headers={"If-None-Match": if_none_match})

    assert response.status_code == 200


def test_get_by_id_changed_pokemon_returns_200_with_new_etag(
    client: TestClient,
) -> None:
    old_etag = client.get("/pokemon/644").headers["ETag"]
    _bump_version(644)

    response = client.get("/pokemon/644", headers={"If-None-Match": old_etag})

    assert response.status_code == 200
    new_etag = response.headers["ETag"]
    assert new_etag == '"1"'
    # The client now sends the new ETag and is up to date again
    again = client.get("/pokemon/644", headers={"If-None-Match": new_etag})
    assert again.status_code == 304


def test_get_by_id_etag_belongs_to_one_pokemon_version(client: TestClient) -> None:
    _bump_version(644)

    zekrom = client.get("/pokemon/644")
    snivy = client.get("/pokemon/495")

    assert zekrom.headers["ETag"] == '"1"'
    assert snivy.headers["ETag"] == '"0"'


def test_get_by_id_not_found_with_if_none_match_is_still_404(
    client: TestClient,
) -> None:
    response = client.get("/pokemon/999999", headers={"If-None-Match": '"0"'})

    assert response.status_code == 404
    assert "ETag" not in response.headers
