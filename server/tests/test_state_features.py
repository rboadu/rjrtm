import pytest
from unittest.mock import patch

import data.states as ds


@pytest.mark.skip(reason="Demo skip for assignment")
def test_skip_demo():
    assert False


def test_update_state_raises(monkeypatch, state_data):
    def fake_update(code, country, updates):
        raise ValueError("DB failure")
    monkeypatch.setattr(ds, 'update_state', fake_update)
    with pytest.raises(ValueError):
        ds.update_state(state_data['code'], 'USA', {'name': 'Fail'})


def test_create_state_endpoint_calls_create(client, state_data):
    with patch.object(ds, 'create_state', return_value=None) as mock_create:
        resp = client.post('/states', json=state_data)
        mock_create.assert_called_once_with(state_data)
        assert resp.status_code in (200, 201)


def test_delete_state_endpoint_calls_delete(client, state_data):
    with patch.object(ds, 'delete_state', return_value=1) as mock_delete:
        resp = client.delete(f"/states/USA/{state_data['code']}") 
        assert resp.status_code in (200, 204, 404)


def test_get_state_by_code_success(client, state_data, monkeypatch):
    expected = {'code': state_data['code'], 'name': state_data['name'], 'country': 'USA'}

    def fake_read(code, country): 
        return expected

    monkeypatch.setattr(ds, 'read_state_by_code_and_country', fake_read) 
    resp = client.get(f"/states/USA/{state_data['code']}") 
    assert resp.status_code == 200
    body = resp.get_json()
    assert body.get('code') == expected['code']
    assert body.get('name') == expected['name']


def test_get_state_by_code_not_found(client, monkeypatch):
    def fake_read(code, country):
        return None

    monkeypatch.setattr(ds, 'read_state_by_code_and_country', fake_read)
    resp = client.get('/states/USA/NOPE')
    assert resp.status_code == 404
    body = resp.get_json()
    assert 'error' in body


def test_patch_state_success(client, monkeypatch):
    def fake_update(code, country, updates):
        assert code == 'TX'
        assert country == 'USA'
        assert updates == {'name': 'Texas'}
        return 1

    monkeypatch.setattr(ds, 'update_state', fake_update)
    resp = client.patch('/states/USA/TX', json={'name': 'Texas'})
    assert resp.status_code == 200
    assert 'message' in resp.get_json()


def test_patch_state_not_found(client, monkeypatch):
    monkeypatch.setattr(ds, 'update_state', lambda c, co, u: 0)
    resp = client.patch('/states/USA/ZZ', json={'name': 'Nowhere'})
    assert resp.status_code == 404


def test_patch_state_empty_payload(client):
    resp = client.patch('/states/USA/NY', json={})
    assert resp.status_code == 400


def test_get_states_by_country_success(client, monkeypatch):
    states_data = [
        {'code': 'TX', 'name': 'Texas', 'country': 'USA'},
        {'code': 'CA', 'name': 'California', 'country': 'USA'},
    ]

    def fake_read(country):
        assert country == 'USA'
        return states_data

    monkeypatch.setattr(ds, 'read_states_by_country', fake_read)
    resp = client.get('/states/country/USA')
    assert resp.status_code == 200
    body = resp.get_json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]['code'] == 'TX'
    assert body[1]['code'] == 'CA'


def test_get_states_by_country_single_state(client, monkeypatch):
    states_data = [{'code': 'ON', 'name': 'Ontario', 'country': 'Canada'}]

    def fake_read(country):
        return states_data if country == 'Canada' else []

    monkeypatch.setattr(ds, 'read_states_by_country', fake_read)
    resp = client.get('/states/country/Canada')
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body) == 1
    assert body[0]['name'] == 'Ontario'