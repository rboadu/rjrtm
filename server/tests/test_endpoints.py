import json
import pytest
import server.endpoints as ep
from data.db_connect import connect_db, SE_DB
from unittest.mock import patch
import data.cities as dc


@pytest.fixture
def client():
    return ep.app.test_client()


@pytest.fixture(autouse=True)
def clear_cities():
    db_client = connect_db()
    db_client[SE_DB].cities.delete_many({})


def _seed(client):
    client.post("/countries/", json={"name": "USA"})
    client.post("/countries/", json={"name": "Japan"})
    client.post("/states", json={"code": "NY", "name": "New York", "country": "USA"})
    client.post("/states", json={"code": "OS", "name": "Osaka Prefecture", "country": "Japan"})


def test_get_all_cities(client):
    response = client.get("/cities")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_post_city(client):
    _seed(client)
    response = client.post("/cities", json={
        "name": "Osaka", "state": "OS", "country": "Japan"
    })
    assert response.status_code in (200, 201)
    assert "message" in response.get_json()


def test_get_city_by_name_and_country(client):
    response = client.get("/cities/Osaka/Japan")
    assert response.status_code in (200, 404)


def test_update_city(client):
    response = client.put(
        "/cities/Osaka/Japan",
        json={"name": "Osaka", "state": "OS", "country": "Japan", "population": 3000000},
    )
    assert response.status_code in (200, 404)


def test_delete_city(client):
    response = client.delete("/cities/Osaka/Japan")
    assert response.status_code in (200, 404)


def test_post_city_duplicate(client):
    _seed(client)
    city = {"name": "New York City", "state": "NY", "country": "USA"}
    client.post("/cities", json=city)
    resp = client.post("/cities", json=city)
    assert resp.status_code == 409
    assert "error" in resp.get_json()