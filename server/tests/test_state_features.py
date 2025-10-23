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
