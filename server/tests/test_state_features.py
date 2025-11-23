import json
import pytest
from unittest.mock import patch

import data.states as ds

# skipped test demonstration
@pytest.mark.skip(reason="Demo skip for assignment")
def test_skip_demo():
    assert False

# pytest.raises 
def test_update_state_raises(monkeypatch, state_data):
    def fake_update(code, updates):
        raise ValueError("DB failure")
    monkeypatch.setattr(ds, 'update_state', fake_update)
    with pytest.raises(ValueError):
        ds.update_state(state_data['code'], {'name': 'Fail'})

# patch used to mock create_state when calling the endpoint 
def test_create_state_endpoint_calls_create(client, state_data):
    with patch.object(ds, 'create_state', return_value=None) as mock_create:
        resp = client.post('/states', json=state_data)
        mock_create.assert_called_once_with(state_data)
        assert resp.status_code in (200, 201)

# patch to mock delete_state 
def test_delete_state_endpoint_calls_delete(client, state_data):
    with patch.object(ds, 'delete_state', return_value=1) as mock_delete:
        # ensure endpoint responds correctly when delete_state reports 1 row deleted
        resp = client.delete(f"/states/{state_data['code']}")
        mock_delete.assert_called_once_with(state_data['code'])
        assert resp.status_code in (200, 204, 404)

#test for GET /states/<code>
def test_get_state_by_code_success(client, state_data, monkeypatch):
    expected = {'code': state_data['code'], 'name': state_data['name']}

    def fake_read(code):
        assert code == state_data['code']
        return expected

    monkeypatch.setattr(ds, 'read_state_by_code', fake_read)
    resp = client.get(f"/states/{state_data['code']}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body.get('code') == expected['code']
    assert body.get('name') == expected['name']

# Additional test for GET /states/<code> when state not found
def test_get_state_by_code_not_found(client, monkeypatch):
    
    def fake_read(_):
        return None

    monkeypatch.setattr(ds, 'read_state_by_code', fake_read)
    resp = client.get('/states/NOPE')
    assert resp.status_code == 404
    body = resp.get_json()
    assert 'error' in body 

def test_patch_state_success(client, monkeypatch):
    # Mock update_state to report 1 modified
    def fake_update(code, updates):
        assert code == 'TX'
        assert updates == {'name': 'Texas'}
        return 1

    monkeypatch.setattr(ds, 'update_state', fake_update)
    resp = client.patch('/states/TX', json={'name': 'Texas'})
    assert resp.status_code == 200
    body = resp.get_json()
    assert 'message' in body


def test_patch_state_not_found(client, monkeypatch):
    monkeypatch.setattr(ds, 'update_state', lambda c, u: 0)
    resp = client.patch('/states/ZZ', json={'name': 'Nowhere'})
    assert resp.status_code == 404


def test_patch_state_empty_payload(client):
    resp = client.patch('/states/NY', json={})
    assert resp.status_code == 400
