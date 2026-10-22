"""Integration tests for `GET /pokemon` (search with query parameters and paging)."""

from fastapi.testclient import TestClient


def test_get_first_page(client: TestClient) -> None:
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


def test_get_second_page(client: TestClient) -> None:
    response = client.get("/pokemon", params={"page": 1})

    body = response.json()
    assert len(body["content"]) == 2
    assert body["page"]["number"] == 1


def test_get_by_type_matches_type_1_or_type_2(client: TestClient) -> None:
    response = client.get("/pokemon", params={"type": "Fire"})

    names = {pokemon["name"] for pokemon in response.json()["content"]}
    assert names == {"Victini", "Tepig", "Chandelure", "Reshiram"}


def test_get_by_name_part_is_case_insensitive(client: TestClient) -> None:
    response = client.get("/pokemon", params={"name": "ZO"})

    names = {pokemon["name"] for pokemon in response.json()["content"]}
    assert names == {"Zorua", "Zoroark"}


def test_get_by_legendary_flag(client: TestClient) -> None:
    response = client.get("/pokemon", params={"legendary": True})

    names = {pokemon["name"] for pokemon in response.json()["content"]}
    assert names == {"Victini", "Reshiram", "Zekrom", "Kyurem"}


def test_get_legendary_second_page(client: TestClient) -> None:
    response = client.get("/pokemon", params={"legendary": True, "size": 2, "page": 1})

    names = [pokemon["name"] for pokemon in response.json()["content"]]
    assert names == ["Zekrom", "Kyurem"]


def test_get_combines_filters(client: TestClient) -> None:
    response = client.get("/pokemon", params={"type": "Dragon", "legendary": True})

    names = {pokemon["name"] for pokemon in response.json()["content"]}
    assert names == {"Reshiram", "Zekrom", "Kyurem"}


def test_get_without_result_returns_empty_page(client: TestClient) -> None:
    response = client.get("/pokemon", params={"name": "does-not-exist"})

    assert response.status_code == 200
    body = response.json()
    assert body["content"] == []
    assert body["page"]["total_elements"] == 0
    assert body["page"]["total_pages"] == 0


def test_get_with_unknown_parameter_is_rejected(client: TestClient) -> None:
    response = client.get("/pokemon", params={"foo": "bar"})

    assert response.status_code == 422


def test_get_with_invalid_type_is_rejected(client: TestClient) -> None:
    response = client.get("/pokemon", params={"type": "Nonsense"})

    assert response.status_code == 422


def test_get_with_size_zero_is_rejected(client: TestClient) -> None:
    response = client.get("/pokemon", params={"size": 0})

    assert response.status_code == 422


def test_get_with_negative_page_is_rejected(client: TestClient) -> None:
    response = client.get("/pokemon", params={"page": -1})

    assert response.status_code == 422
