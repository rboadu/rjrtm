import json
import pytest
import server.endpoints as ep
from unittest.mock import patch
import data.states as ds


def test_get_all_states(client):
    response = client.get("/states")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_post_state(client):
    with patch.object(ds, 'create_state', return_value="fake_id"):
        new_state = {"name": "California", "code": "CA", "country": "USA"}
        response = client.post("/states", json=new_state)
        assert response.status_code in (200, 201)
        assert "message" in response.get_json()


def test_get_state_by_country_and_code(client):
    response = client.get("/states/USA/CA")
    assert response.status_code in (200, 404)


def test_update_state(client):
    response = client.put(
        "/states/USA/CA",
        json={"code": "CA", "name": "California", "country": "USA"},
    )
    assert response.status_code in (200, 404)


def test_delete_state(client):
    response = client.delete("/states/USA/CA")
    assert response.status_code in (200, 404)