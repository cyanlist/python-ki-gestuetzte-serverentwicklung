"""Integration tests for `GET /pokemon/{pokemon_id}`."""

import pytest
from fastapi.testclient import TestClient

SEED_IDS = [494, 495, 498, 501, 570, 571, 609, 612, 635, 643, 644, 646]
"""The Pokédex numbers of the seed data (`02-seed.sql`)."""


def test_get_by_id_returns_pokemon(client: TestClient) -> None:
    response = client.get("/pokemon/644")

    assert response.status_code == 200
    body = response.json()
    # The order of the moves is not defined, so they are compared by name
    moves = sorted(body.pop("moves"), key=lambda move: move["name"])
    assert body == {
        "id": 644,
        "name": "Zekrom",
        "type_1": "Dragon",
        "type_2": "Electric",
        "height_m": 2.9,
        "weight_kg": 345.0,
        "legendary": True,
        "detail": {"catch_rate": 3, "base_experience": 306},
    }
    assert moves == [
        {"name": "Dragon Claw", "type": "Dragon", "power": 80, "accuracy": 100},
        {"name": "Thunderbolt", "type": "Electric", "power": 90, "accuracy": 100},
    ]


def test_get_by_id_pokemon_with_one_type(client: TestClient) -> None:
    response = client.get("/pokemon/495")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Snivy"
    assert body["type_1"] == "Grass"
    assert body["type_2"] is None


def test_get_by_id_does_not_expose_internal_fields(client: TestClient) -> None:
    response = client.get("/pokemon/644")

    body = response.json()
    assert "version" not in body
    assert "updated_at" not in body
    assert "created_at" not in body


@pytest.mark.parametrize("pokemon_id", SEED_IDS)
def test_get_by_id_all_seed_pokemon(client: TestClient, pokemon_id: int) -> None:
    response = client.get(f"/pokemon/{pokemon_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == pokemon_id
    assert body["detail"] is not None
    assert len(body["moves"]) >= 1


def test_get_by_id_not_found(client: TestClient) -> None:
    response = client.get("/pokemon/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "No Pokémon with the number 999999"}


def test_get_by_id_number_of_another_generation_is_not_found(
    client: TestClient,
) -> None:
    # 25 (Pikachu) is not part of the seed data
    response = client.get("/pokemon/25")

    assert response.status_code == 404


@pytest.mark.parametrize("pokemon_id", ["abc", "1.5", "1e3", "-"])
def test_get_by_id_invalid_number(client: TestClient, pokemon_id: str) -> None:
    response = client.get(f"/pokemon/{pokemon_id}")

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert errors[0]["loc"] == ["path", "pokemon_id"]
