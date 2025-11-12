import pytest
import data.db_connect as db_connect

def test_connect_db_success():
    client = db_connect.connect_db()
    assert client is not None
    assert isinstance(client.list_database_names(), list)

def test_connect_db_failure(monkeypatch):
    """Simulate MongoDB connection failure and verify proper exception."""
    db_connect.client = None

    def mock_client(*args, **kwargs):
        raise ConnectionError("Failed to connect")

    monkeypatch.setattr("data.db_connect.pm.MongoClient", mock_client)

    with pytest.raises(ConnectionError):
        db_connect.connect_db()
