import json
import pytest
from unittest.mock import patch

import data.states as ds
import server.endpoints as ep


@pytest.fixture
def client():
    return ep.app.test_client()


def test_post_state_with_country_calls_create(client):
    new_state = {"code": "FL", "name": "Florida", "country": "USA"}
    with patch.object(ds, 'create_state', return_value=None) as mock_create:
        resp = client.post('/states', json=new_state)
        mock_create.assert_called_once_with(new_state)
        assert resp.status_code in (200, 201)


def test_get_state_includes_country_when_present(client, monkeypatch):
    expected = {"code": "FL", "name": "Florida", "country": "USA"}

    def fake_read(code):
        assert code == expected['code']
        return expected

    monkeypatch.setattr(ds, 'read_state_by_code', fake_read)
    resp = client.get(f"/states/{expected['code']}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body.get('code') == expected['code']
    assert body.get('country') == expected['country']
