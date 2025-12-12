import json
import pytest
from unittest.mock import patch

import data.states as ds

# skipped test demonstration
@pytest.mark.skip(reason="Demo skip for assignment")
def test_skip_demo():
    assert False

# patch to mock delete_state 
def test_delete_state_endpoint_calls_delete(client, state_data):
    with patch.object(ds, 'delete_state', return_value=1) as mock_delete:
        # ensure endpoint responds correctly when delete_state reports 1 row deleted
        resp = client.delete(f"/states/{state_data['code']}")
        mock_delete.assert_called_once_with(state_data['code'])
        assert resp.status_code in (200, 204, 404)
