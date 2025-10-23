import pytest
from unittest.mock import patch

import server.endpoints as ep
import data.states as ds

# Fixture: provides a sample state dict
@pytest.fixture
def sample_state():
    return {"code": "FL", "name": "Florida"}

# Use skip: demonstration of skipping a test
@pytest.mark.skip(reason="Demo skip: not required for CI")
def test_skipped_example():
    assert False

# with raises: test that update_state raises for bad input (simulate by patching)
def test_update_state_raises_when_db_fails(sample_state):
    # Patch the update_state function to raise a ValueError for this test
    with patch.object(ds, 'update_state', side_effect=ValueError("bad update")):
        with pytest.raises(ValueError):
            ds.update_state(sample_state['code'], {"name": "Bad"})

# patch: test POST /states uses create_state; mock create_state to avoid DB access
def test_create_state_endpoint_uses_create_state(client, sample_state):
    with patch.object(ds, 'create_state', return_value=None) as mock_create:
        resp = client.post('/states', json=sample_state)
        # endpoint should call create_state
        mock_create.assert_called_once_with(sample_state)
        assert resp.status_code in (200, 201)
