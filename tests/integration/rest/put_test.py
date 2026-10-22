"""Integration tests for `PUT /pokemon/{pokemon_id}` (optimistic locking)."""

from typing import Any, Final

from fastapi.testclient import TestClient

ZEKROM: Final[dict[str, Any]] = {
    "name": "Zekrom",
    "type_1": "Dragon",
    "type_2": "Electric",
    "height_m": 3.0,
    "weight_kg": 345.0,
    "legendary": True,
}


def test_put_replaces_pokemon_and_returns_new_etag(client: TestClient) -> None:
    etag = client.get("/pokemon/644").headers["ETag"]

    response = client.put("/pokemon/644", json=ZEKROM, headers={"If-Match": etag})

    assert response.status_code == 204
    assert response.headers["ETag"] == '"1"'
    assert response.content == b""
    assert client.get("/pokemon/644").json()["height_m"] == 3.0


def test_put_without_if_match_requires_precondition(client: TestClient) -> None:
    response = client.put("/pokemon/644", json=ZEKROM)

    assert response.status_code == 428


def test_put_malformed_if_match_fails_precondition(client: TestClient) -> None:
    response = client.put("/pokemon/644", json=ZEKROM, headers={"If-Match": "abc"})

    assert response.status_code == 412


def test_put_unquoted_if_match_fails_precondition(client: TestClient) -> None:
    response = client.put("/pokemon/644", json=ZEKROM, headers={"If-Match": "0"})

    assert response.status_code == 412


def test_put_outdated_version_is_lost_update(client: TestClient) -> None:
    headers = {"If-Match": '"0"'}
    first = client.put("/pokemon/644", json=ZEKROM, headers=headers)
    assert first.status_code == 204

    # The same (now outdated) version is sent again: this is the lost update
    second = client.put("/pokemon/644", json=ZEKROM, headers=headers)

    assert second.status_code == 412


def test_put_unknown_id_is_not_found(client: TestClient) -> None:
    response = client.put("/pokemon/999999", json=ZEKROM, headers={"If-Match": '"0"'})

    assert response.status_code == 404


def test_put_name_of_another_pokemon_is_conflict(client: TestClient) -> None:
    response = client.put(
        "/pokemon/644",
        json={**ZEKROM, "name": "Reshiram"},
        headers={"If-Match": '"0"'},
    )

    assert response.status_code == 409


def test_put_keeping_own_name_is_allowed(client: TestClient) -> None:
    response = client.put(
        "/pokemon/644",
        json={**ZEKROM, "name": "Zekrom"},
        headers={"If-Match": '"0"'},
    )

    assert response.status_code == 204


def test_put_invalid_data_is_rejected(client: TestClient) -> None:
    response = client.put(
        "/pokemon/644",
        json={**ZEKROM, "height_m": -1},
        headers={"If-Match": '"0"'},
    )

    assert response.status_code == 422


def test_put_does_not_change_detail_or_moves(client: TestClient) -> None:
    before = client.get("/pokemon/644").json()

    client.put("/pokemon/644", json=ZEKROM, headers={"If-Match": '"0"'})

    after = client.get("/pokemon/644").json()
    assert after["detail"] == before["detail"]
    assert after["moves"] == before["moves"]
