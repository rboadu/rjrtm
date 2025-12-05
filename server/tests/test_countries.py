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

def test_get_country_by_code_not_found(client):
    """Test retrieval of non-existent country."""
    with patch('server.routes.countries.read_country_by_code', return_value=None):
        response = client.get('/countries/XX')
        assert response.status_code == 404

def test_get_country_invalid_code_format(client):
    """Test invalid country code format."""
    response = client.get('/countries/us')  # are lowercase # should fail
    assert response.status_code == 400
    
    response = client.get('/countries/U')  # too short # should fail
    assert response.status_code == 400
    
    response = client.get('/countries/U2')  # contains number # should fail
    assert response.status_code == 400

def test_get_country_three_letter_code(client):
    """Test retrieval of country with 3-letter code (e.g., USA)."""
    mock_country = {"_id": "507f1f77bcf86cd799439011", "code": "USA", "name": "United States"}
    
    with patch('server.routes.countries.read_country_by_code', return_value=mock_country):
        response = client.get('/countries/USA')
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 'USA'
        assert data['name'] == 'United States'

def test_search_countries_success(client):
    """Test successful search for countries by name."""
    mock_countries = [
        {"_id": "507f1f77bcf86cd799439011", "code": "US", "name": "United States"},
        {"_id": "507f191e810c19729de860ea", "code": "GB", "name": "United Kingdom"}
    ]
    
    with patch('server.routes.countries.search_countries_by_name', return_value=mock_countries):
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
