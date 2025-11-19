import pytest
from unittest.mock import patch

def test_get_countries_success(client):
    """Test successful retrieval of all countries."""
    mock_countries = [
        {"_id": "507f1f77bcf86cd799439011", "code": "US", "name": "United States"},
        {"_id": "507f191e810c19729de860ea", "code": "UK", "name": "United Kingdom"}
    ]
    
    with patch('server.routes.countries.read_all_countries', return_value=mock_countries):
        response = client.get('/countries/')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['code'] == 'US'

def test_get_country_by_code_success(client):
    """Test successful retrieval of a country by code."""
    mock_country = {"_id": "507f1f77bcf86cd799439011", "code": "US", "name": "United States"}
    
    with patch('server.routes.countries.read_country_by_code', return_value=mock_country):
        response = client.get('/countries/US')
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 'US'
        assert data['name'] == 'United States'
