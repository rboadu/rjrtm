# data/tests/test_cities.py
"""
Unit tests for the cities data access layer.
"""
import pytest
import data.cities as dc

@pytest.fixture
def sample_city():
    """Provide a sample city dictionary."""
    return {"name": "Tokyo", "country": "Japan", "population": 14000000}

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up Tokyo after each test to prevent conflicts."""
    yield
    # Clean up after the test runs
    try:
        dc.delete_city("Tokyo", "Japan")
    except:
        pass  # Ignore if it doesn't exist

def test_add_city(sample_city):
    """Test adding a new city."""
    result = dc.add_city(sample_city)
    assert result == sample_city

def test_get_city_by_name(sample_city):
    """Test retrieving a city by name."""
    dc.add_city(sample_city)
    city = dc.get_city_by_name("Tokyo")
    assert city is not None
    assert city["name"] == "Tokyo"
    assert city["country"] == "Japan"

def test_update_city(sample_city):
    """Test updating an existing city."""
    dc.add_city(sample_city)
    updated = {"population": 15000000}
    success = dc.update_city("Tokyo", "Japan", updated)  # ✅ Fixed: Added "Japan" parameter
    assert success

def test_delete_city(sample_city):
    """Test deleting a city."""
    dc.add_city(sample_city)
    success = dc.delete_city("Tokyo", "Japan")  # ✅ Fixed: Added "Japan" parameter
    assert success