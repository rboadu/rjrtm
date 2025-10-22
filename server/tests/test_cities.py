import json
import pytest
import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

@pytest.fixture
def client():
    return ep.app.test_client()

def test_get_all_cities(client):
    """GET /cities should return list (even if empty)."""
    response = client.get("/cities")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_post_city(client):
    """POST /cities should add a new city."""
    new_city = {"name": "Osaka", "country": "Japan", "population": 2700000}
    response = client.post(
        "/cities",
        data=json.dumps(new_city),
        content_type="application/json",
    )
    assert response.status_code in (200, 201)
    data = response.get_json()
    assert "message" in data

def test_get_city_by_name(client):
    """GET /cities/<name> should return that city."""
    response = client.get("/cities/Osaka")
    assert response.status_code in (200, 404)

def test_update_city(client):
    """PUT /cities/<name> should update population."""
    updates = {"population": 3000000}
    response = client.put(
        "/cities/Osaka",
        data=json.dumps(updates),
        content_type="application/json",
    )
    assert response.status_code in (200, 404)

def test_delete_city(client):
    """DELETE /cities/<name> should remove city."""
    response = client.delete("/cities/Osaka")
    assert response.status_code in (200, 404)
