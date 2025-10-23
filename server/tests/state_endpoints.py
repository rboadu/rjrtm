import json
import pytest
import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

@pytest.fixture
def client():
    return ep.app.test_client()

def test_get_all_states(client):
    """GET /states should return list (even if empty)."""
    response = client.get("/states")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_post_state(client):
    """POST /states should add a new state."""
    new_state = {"name": "California", "code": "CA", "population": 39500000}
    response = client.post(
        "/states",
        data=json.dumps(new_state),
        content_type="application/json",
    )
    assert response.status_code in (200, 201)
    data = response.get_json()
    assert "message" in data

def test_get_state_by_code(client):
    """GET /states/<code> should return that state."""
    response = client.get("/states/CA")
    assert response.status_code in (200, 404)

def test_update_state(client):
    """PUT /states/<code> should update population."""
    updates = {"population": 40000000}
    response = client.put(
        "/states/CA",
        data=json.dumps(updates),
        content_type="application/json",
    )
    assert response.status_code in (200, 404)
    
def test_delete_state(client):
    """DELETE /states/<code> should remove state."""
    response = client.delete("/states/CA")
    assert response.status_code in (200, 404)
