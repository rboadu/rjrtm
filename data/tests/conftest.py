import pytest
from data.db_connect import connect_db, SE_DB

@pytest.fixture(autouse=True)
def clear_db_each_test():
    client = connect_db()
    client.drop_database(SE_DB)
