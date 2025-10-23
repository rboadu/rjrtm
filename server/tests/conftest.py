import pytest
import server.endpoints as ep

#Fixture to provide a test client for the endpoints
@pytest.fixture
def client():
    return ep.app.test_client()

@pytest.fixture
def state_data():
    return {"code": "TX", "name": "Texas"}
