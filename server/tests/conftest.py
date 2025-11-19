import pytest
import server.endpoints as ep
import data.cities as dc

#Fixture to provide a test client for the endpoints
@pytest.fixture
def client():
    return ep.app.test_client()

@pytest.fixture
def state_data():
    return {"code": "TX", "name": "Texas"}

# Automatically clear in-memory city data before each test
@pytest.fixture(autouse=True)
def clear_city_data():
    """Automatically clear in-memory city data before each test to avoid cross-test pollution."""
    # Check common attribute names for the in-memory database
    if hasattr(dc, "CITIES_DB"):
        dc.CITIES_DB.clear()
    elif hasattr(dc, "cities"):
        dc.cities.clear()
    elif hasattr(dc, "CITY_DATA"):
        dc.CITY_DATA.clear()
    elif hasattr(dc, "CITY_DB"):
        dc.CITY_DB.clear()
    else:
        # As a fallback, try to reset via a helper if it exists
        if hasattr(dc, "reset"):
            dc.reset()
    yield