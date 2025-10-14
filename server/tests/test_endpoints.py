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
    return ep.app.test_client()

def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


def test_journal():
    resp = TEST_CLIENT.get(ep.JOURNAL_EP)
    resp_json = resp.get_json()
    assert ep.JOURNAL_RESP in resp_json
    assert resp_json[ep.JOURNAL_RESP] == 'RJRTM Journal'

def test_journal_add(client):
    response = client.post('/journal/add', json={'entry': 'My first journal entry'})
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json['message'] == 'Entry added'
    assert resp_json['entry'] == 'My first journal entry'