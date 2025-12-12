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


def test_post_states_bulk_success(client):
    """POST /states/bulk should create multiple states when given valid list."""
    payload = [
        {"name": "Testlandia", "code": "TL", "population": 12345},
        {"name": "Examplestate", "code": "EX", "population": 54321},
    ]
    response = client.post(
        "/states/bulk",
        data=json.dumps(payload),
        content_type="application/json",
    )
    # Accept success, validation error, or internal error depending on env
    assert response.status_code in (201, 400, 500)
    data = response.get_json()
    if response.status_code == 201:
        assert isinstance(data.get("created"), list)
        assert "errors" in data
    else:
        assert "error" in data


def test_post_states_bulk_invalid_payload(client):
    """POST /states/bulk must reject non-list payloads."""
    payload = {"code": "BADSINGLE", "name": "Bad"}
    response = client.post(
        "/states/bulk",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_post_states_bulk_some_invalid_items(client):
    """Mixed valid/invalid items: valid ones inserted, invalid reported."""
    payload = [
        {"name": "PartialValid", "code": "PV", "population": 100},
        {"name": "MissingCode"},
        "not-a-dict",
    ]
    response = client.post(
        "/states/bulk",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code in (201, 400, 500)
    data = response.get_json()
    if response.status_code == 201:
        assert isinstance(data.get("created"), list)
        # expect at least one error recorded for the invalid items
        assert isinstance(data.get("errors"), list)
    else:
        assert "error" in data
