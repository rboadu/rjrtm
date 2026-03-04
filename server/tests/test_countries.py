import pytest
from unittest.mock import patch


def test_get_countries_success(client):
    mock_countries = [
        {"name": "United States"},
        {"name": "United Kingdom"}
    ]
    with patch('server.endpoints.read_all_countries', return_value=mock_countries):
        response = client.get('/countries/')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['name'] == 'United States'


def test_get_country_by_name_success(client):
    mock_country = {"name": "United States"}
    with patch('server.endpoints.read_country_by_name', return_value=mock_country):
        response = client.get('/countries/United States')
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'United States'


def test_get_country_by_name_not_found(client):
    with patch('server.endpoints.read_country_by_name', return_value=None):
        response = client.get('/countries/Fakeland')
        assert response.status_code == 404


def test_get_country_by_name_returns_404_for_unknown(client):
    response = client.get('/countries/Nonexistentcountry')
    assert response.status_code == 404


def test_search_countries_success(client):
    mock_countries = [
        {"name": "United States"},
        {"name": "United Kingdom"}
    ]
    with patch('server.endpoints.search_countries_by_name', return_value=mock_countries):
        response = client.get('/countries/search?q=united')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['name'] == 'United States'
        assert data[1]['name'] == 'United Kingdom'


def test_search_countries_missing_query(client):
    response = client.get('/countries/search')
    assert response.status_code == 400


def test_create_country_success(client):
    payload = {"name": "Canada"}
    mock_id = "507f1f77bcf86cd799439012"
    with patch('server.endpoints.create_country', return_value=mock_id) as mock_create:
        response = client.post('/countries/', json=payload)
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Country created"
        assert data["country"]["name"] == "Canada"
        mock_create.assert_called_once_with(payload)


def test_create_country_duplicate(client):
    with patch('server.endpoints.create_country', side_effect=ValueError("already exists")):
        response = client.post('/countries/', json={"name": "Canada"})
        assert response.status_code == 409
        assert "error" in response.get_json()


def test_delete_country_success(client):
    with patch('server.endpoints.delete_country_by_name', return_value=1):
        response = client.delete('/countries/Canada')
        assert response.status_code == 200
        assert response.get_json()["message"] == "Country deleted"


def test_delete_country_not_found(client):
    with patch('server.endpoints.delete_country_by_name', return_value=0):
        response = client.delete('/countries/Atlantis')
        assert response.status_code == 404