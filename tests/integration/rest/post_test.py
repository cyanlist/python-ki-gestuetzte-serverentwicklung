"""Integration tests for `POST /pokemon`."""

from typing import Any, Final

import pytest
from fastapi.testclient import TestClient

NEW_POKEMON: Final[dict[str, Any]] = {
    "id": 600,
    "name": "Testmon",
    "type_1": "Fire",
    "type_2": None,
    "height_m": 1.2,
    "weight_kg": 30.5,
    "legendary": False,
    "detail": {"catch_rate": 100, "base_experience": 150},
    "moves": [{"name": "Ember", "type": "Fire", "power": 40, "accuracy": 100}],
}


def test_post_creates_pokemon(client: TestClient) -> None:
    response = client.post("/pokemon", json=NEW_POKEMON)

    assert response.status_code == 201
    location = response.headers["Location"]
    assert location.endswith("/pokemon/600")
    assert response.content == b""

    created = client.get(location).json()
    assert created["name"] == "Testmon"
    assert created["type_1"] == "Fire"
    assert created["detail"] == {"catch_rate": 100, "base_experience": 150}
    assert created["moves"] == [
        {"name": "Ember", "type": "Fire", "power": 40, "accuracy": 100}
    ]


def test_post_without_moves_defaults_to_empty_list(client: TestClient) -> None:
    data = {k: v for k, v in NEW_POKEMON.items() if k != "moves"}

    response = client.post("/pokemon", json=data)

    assert response.status_code == 201
    created = client.get(response.headers["Location"]).json()
    assert created["moves"] == []


def test_post_existing_id_is_conflict(client: TestClient) -> None:
    response = client.post("/pokemon", json={**NEW_POKEMON, "id": 644})

    assert response.status_code == 409


def test_post_existing_name_is_conflict(client: TestClient) -> None:
    response = client.post("/pokemon", json={**NEW_POKEMON, "name": "Zekrom"})

    assert response.status_code == 409


@pytest.mark.parametrize(
    "changes",
    [
        {"id": 100},
        {"id": 650},
        {"name": ""},
        {"type_1": "Nonsense"},
        {"height_m": -1},
        {"height_m": 0},
        {"weight_kg": -1},
        {"detail": {"catch_rate": 0, "base_experience": 1}},
        {"detail": {"catch_rate": 256, "base_experience": 1}},
        {"detail": {"catch_rate": 100, "base_experience": 0}},
        {"detail": None},
        {"moves": [{"name": "X", "type": "Fire", "power": 0, "accuracy": 100}]},
        {"moves": [{"name": "X", "type": "Fire", "power": 1, "accuracy": 0}]},
        {
            "moves": [
                {"name": f"Move {i}", "type": "Fire", "power": 1, "accuracy": 1}
                for i in range(5)
            ]
        },
        {"unknown_field": 1},
    ],
    ids=[
        "id-too-low",
        "id-too-high",
        "empty-name",
        "invalid-type",
        "negative-height",
        "zero-height",
        "negative-weight",
        "catch-rate-too-low",
        "catch-rate-too-high",
        "base-experience-too-low",
        "missing-detail",
        "move-power-zero",
        "move-accuracy-zero",
        "too-many-moves",
        "unknown-field",
    ],
)
def test_post_invalid_data_is_rejected(
    client: TestClient, changes: dict[str, Any]
) -> None:
    response = client.post("/pokemon", json={**NEW_POKEMON, **changes})

    assert response.status_code == 422


def test_post_broken_json_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/pokemon",
        content="{broken",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
