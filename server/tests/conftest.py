import pytest
import server.endpoints as ep
from data.db_connect import connect_db, SE_DB

# --------------------------------------------------
# Flask test client
# --------------------------------------------------
@pytest.fixture
def client():
    return ep.app.test_client()


# --------------------------------------------------
# Sample state data (used by endpoint tests)
# --------------------------------------------------
@pytest.fixture
def state_data():
    return {"code": "TX", "name": "Texas"}


# --------------------------------------------------
# MongoDB cleanup (REAL, not fake in-memory)
# Runs before every test to prevent state leakage
# --------------------------------------------------
@pytest.fixture(autouse=True)
def clear_db_each_test():
    client = connect_db()
    client.drop_database(SE_DB)
