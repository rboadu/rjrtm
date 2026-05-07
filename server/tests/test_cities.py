import json
import pytest
import server.endpoints as ep
from data.db_connect import connect_db, SE_DB

TEST_CLIENT = ep.app.test_client()


@pytest.fixture
def client():
    return ep.app.test_client()


@pytest.fixture(autouse=True)
def clear_cities():
    """Clear cities and states collections before each test."""
    db_client = connect_db()
    db_client[SE_DB].cities.delete_many({})
    db_client[SE_DB].states.delete_many({})
    db_client[SE_DB].countries.delete_many({})


def _seed(client):
    """Seed countries and states needed for city creation."""
    client.post("/countries/", json={"name": "USA"})
    client.post("/countries/", json={"name": "Japan"})
    client.post("/states", json={"code": "NY", "name": "New York", "country": "USA"})
    client.post("/states", json={"code": "LA", "name": "Los Angeles", "country": "USA"})
    client.post("/states", json={"code": "NK", "name": "Newark State", "country": "USA"})
    client.post("/states", json={"code": "OS", "name": "Osaka Prefecture", "country": "Japan"})
    client.post("/states", json={"code": "TK", "name": "Tokyo Prefecture", "country": "Japan"})


def test_get_all_cities(client):
    """GET /cities should return list (even if empty)."""
    response = client.get("/cities")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_post_city(client):
    """POST /cities should add a new city."""
    _seed(client)
    response = client.post("/cities", json={
        "name": "Osaka", "state": "OS", "country": "Japan"
    })
    assert response.status_code in (200, 201)
    assert "message" in response.get_json()


def test_get_city_by_name_and_country(client):
    """GET /cities/<name>/<country> should return that city or 404."""
    response = client.get("/cities/Osaka/Japan")
    assert response.status_code in (200, 404)


def test_update_city(client):
    """PUT /cities/<name>/<country> should update city or 404."""
    response = client.put(
        "/cities/Osaka/Japan",
        json={"name": "Osaka", "state": "OS", "country": "Japan", "population": 3000000},
    )
    assert response.status_code in (200, 404)


def test_delete_city(client):
    """DELETE /cities/<name>/<country> should remove city or 404."""
    response = client.delete("/cities/Osaka/Japan")
    assert response.status_code in (200, 404)


def test_post_city_duplicate(client):
    """POST /cities should return 409 for duplicate city."""
    _seed(client)
    city = {"name": "Osaka", "state": "OS", "country": "Japan"}
    client.post("/cities", json=city)
    resp = client.post("/cities", json=city)
    assert resp.status_code == 409
    assert "error" in resp.get_json()


def test_post_city_missing_name_or_country(client):
    """POST /cities should reject requests missing required fields."""
    resp = client.post("/cities", json={"population": 500000})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

    resp2 = client.post("/cities", json={"name": "NoCountry"})
    assert resp2.status_code == 400
    assert "error" in resp2.get_json()


def test_post_city_invalid_population(client):
    """POST /cities should reject negative population."""
    resp = client.post("/cities", json={
        "name": "GhostTown", "state": "NY", "country": "USA", "population": -123
    })
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_put_city_invalid_population(client):
    """PUT /cities/<name>/<country> should reject negative population."""
    _seed(client)
    client.post("/cities", json={
        "name": "Testville", "state": "NY", "country": "USA", "population": 100
    })
    resp = client.put("/cities/Testville/USA", json={"population": -50})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_post_city_malformed_json(client):
    """POST /cities should return 400 for malformed JSON."""
    bad_json = "{name: 'BadCity', country: 'Nowhere'}"
    resp = client.post("/cities", data=bad_json, content_type="application/json")
    assert resp.status_code == 400


@pytest.mark.parametrize("query,expected_status", [
    ("/cities?name=New", 200),
    ("/cities?min_population=1000000", 200),
    ("/cities?max_population=10000000", 200),
    ("/cities?name=Tokyo&min_population=10000000", 200),
])
def test_filter_cities_advanced_queries(client, query, expected_status):
    """GET /cities should handle advanced query filters."""
    _seed(client)
    sample_cities = [
        {"name": "New York", "state": "NY", "country": "USA", "population": 8419600},
        {"name": "Newark", "state": "NK", "country": "USA", "population": 300000},
        {"name": "Tokyo", "state": "TK", "country": "Japan", "population": 13960000},
    ]
    for city in sample_cities:
        client.post("/cities", json=city)

    resp = client.get(query)
    assert resp.status_code == expected_status
    data = resp.get_json()
    assert isinstance(data, list)

    if "name=" in query:
        name_filter = query.split("name=")[1].split("&")[0].lower()
        assert any(name_filter in c["name"].lower() for c in data)
    if "min_population" in query:
        min_pop = int(query.split("min_population=")[1].split("&")[0])
        assert any(c["population"] >= min_pop for c in data)
    if "max_population" in query:
        max_pop = int(query.split("max_population=")[1].split("&")[0])
        assert any(c["population"] <= max_pop for c in data)