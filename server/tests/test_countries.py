import pytest
from unittest.mock import patch


def test_get_countries_success(client):
    """Test successful retrieval of all countries."""
    mock_countries = [
        {"_id": "507f1f77bcf86cd799439011", "name": "United States"},
        {"_id": "507f191e810c19729de860ea", "name": "United Kingdom"}
    ]
    with patch('server.endpoints.read_all_countries', return_value=mock_countries):
        response = client.get('/countries/')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['name'] == 'United States'


def test_get_country_by_name_success(client):
    """Test successful retrieval of a country by name."""
    mock_country = {"_id": "507f1f77bcf86cd799439011", "name": "United States"}
    with patch('server.endpoints.read_country_by_name', return_value=mock_country):
        response = client.get('/countries/United States')
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'United States'


def test_get_country_by_name_not_found(client):
    """Test retrieval of non-existent country."""
    with patch('server.endpoints.read_country_by_name', return_value=None):
        response = client.get('/countries/Fakeland')
        assert response.status_code == 404


def test_get_country_by_name_returns_404_for_unknown(client):
    """Test that looking up a country name that doesn't exist returns 404."""
    response = client.get('/countries/Nonexistentcountry')
    assert response.status_code == 404


def test_search_countries_success(client):
    """Test successful search for countries by name."""
    mock_countries = [
        {"_id": "507f1f77bcf86cd799439011", "name": "United States"},
        {"_id": "507f191e810c19729de860ea", "name": "United Kingdom"}
    ]
    with patch('server.endpoints.search_countries_by_name', return_value=mock_countries):
        response = client.get('/countries/search?q=united')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['name'] == 'United States'
        assert data[1]['name'] == 'United Kingdom'


def test_search_countries_missing_query(client):
    """Test search endpoint with missing query parameter."""
    response = client.get('/countries/search')
    assert response.status_code == 400


def test_create_country_success(client):
    """Test successful creation of a new country."""
    payload = {"name": "Canada"}
    mock_id = "507f1f77bcf86cd799439012"
    with patch('server.endpoints.create_country', return_value=mock_id) as mock_create:
        response = client.post('/countries/', json=payload)
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Country created successfully"
        assert data["country"]["name"] == "Canada"
        assert data["country"]["_id"] == mock_id
        mock_create.assert_called_once_with(payload)