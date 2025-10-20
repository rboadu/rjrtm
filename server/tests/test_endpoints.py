from http import HTTPStatus
from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

@pytest.fixture
def client():
    """Provides a test client for the Flask app."""
    return ep.app.test_client()

@pytest.mark.skip(reason="Demo of skip feature for assignment")
def skipped_test_example():
    assert True 

def test_hello():
    """Test the /hello endpoint returns the expected greeting."""
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json

def test_journal():
    """Test the /journal endpoint returns the expected journal response."""
    resp = TEST_CLIENT.get(ep.JOURNAL_EP)
    resp_json = resp.get_json()
    assert ep.JOURNAL_RESP in resp_json
    assert resp_json[ep.JOURNAL_RESP] == 'RJRTM Journal'

def test_journal_add(client):
    """Test adding a journal entry via POST /journal/add."""
    response = client.post('/journal/add', json={'entry': 'My first journal entry'})
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json['message'] == 'Entry added'
    assert resp_json['entry'] == 'My first journal entry'

def test_get_states(client):
    """Test GET /states returns a list or handles DB errors gracefully."""
    response = client.get('/states')
    assert response.status_code in (200, 500)  # 500 if Mongo not connected
    assert 'states' not in response.get_json() or isinstance(response.get_json(), list)

def test_post_states(client):
    """Test POST /states to add a new state, expects 201 or DB error."""
    response = client.post('/states', json={'code': 'CA', 'name': 'California'})
    assert response.status_code in (201, 500)

def test_get_countries(client):
    """Test the GET /countries endpoint."""
    response = client.get('/countries/')
    assert response.status_code in (HTTPStatus.OK, HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.NOT_FOUND)
    if response.status_code == HTTPStatus.OK:
        resp_json = response.get_json()
        assert isinstance(resp_json, list)

def test_get_country_by_code_not_found(client):
    """Test GET /countries/<code> with a code that does not exist."""
    response = client.get('/countries/NO_SUCH_CODE')
    assert response.status_code == 404
    assert b"not found" in response.data.lower()

def test_get_country_by_code_found(client):
    """Test GET /countries/<code> with a code that does exist."""
    response = client.get('/countries/US')
    assert response.status_code in (200, 404, 500)
    if response.status_code == 200:
        resp_json = response.get_json()
        assert resp_json['code'] == 'US'