"""
Data access layer for the 'cities' collection in MongoDB.
Uses decorated helper functions to ensure each call has a valid DB connection.
Provides a simple in-memory cache for get_all_cities to reduce DB load.
"""

from typing import Any, Dict, List, Optional

from data.db_connect import (
    create,
    read_one,
    update,
    delete,
    read,
    SE_DB,
    convert_mongo_id,
)

COLLECTION = "cities"

# Simple in-memory cache of all cities.
# Invalidated on any write operation (create, update, delete).
_cities_cache: Optional[List[Dict[str, Any]]] = None


def _invalidate_cache() -> None:
    """Clear the in-memory cache of cities."""
    global _cities_cache
    _cities_cache = None


def get_all_cities() -> List[Dict[str, Any]]:
    """
    Return a list of all cities.

    Results are cached in memory until a write operation
    (add_city, update_city, delete_city) invalidates the cache.
    """
    global _cities_cache

    if _cities_cache is not None:
        return _cities_cache

    cities = read(COLLECTION, db=SE_DB, no_id=False)
    for city in cities:
        convert_mongo_id(city)

    _cities_cache = cities
    return cities


def get_city_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Find a city by its name, or return None if not found."""
    city = read_one(COLLECTION, {"name": name}, db=SE_DB)
    if city:
        convert_mongo_id(city)
    return city


def add_city(city: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new city document and return the created record."""
    result = create(COLLECTION, city, db=SE_DB)
    city["_id"] = str(result.inserted_id)
    _invalidate_cache()
    return city


def update_city(name: str, updated_city: Dict[str, Any]) -> bool:
    """
    Update a city's information.

    Returns True if a document was modified, False otherwise.
    """
    result = update(COLLECTION, {"name": name}, updated_city, db=SE_DB)
    modified = getattr(result, "modified_count", 0) > 0
    if modified:
        _invalidate_cache()
    return modified


def delete_city(name: str) -> bool:
    """
    Delete a city by name.

    Returns True if a document was deleted, False otherwise.
    """
    result = delete(COLLECTION, {"name": name}, db=SE_DB)
    # Depending on your delete helper, result may be a count or an object.
    deleted = False
    if isinstance(result, int):
        deleted = result > 0
    else:
        # e.g., result.deleted_count if using pymongo's DeleteResult
        deleted = getattr(result, "deleted_count", 0) > 0

    if deleted:
        _invalidate_cache()
    return deleted


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
    success = dc.update_city("Tokyo", updated)
    assert success


def test_delete_city(sample_city):
    """Test deleting a city."""
    dc.add_city(sample_city)
    success = dc.delete_city("Tokyo")
    assert success


def test_get_all_cities_with_fake_db(monkeypatch):
    """Test get_all_cities using a fake in-memory DB to avoid real Mongo."""

    class FakeCollection:
        def __init__(self):
            self._docs = []

        def find(self, *args, **kwargs):
            # Return an iterator of docs
            return iter(self._docs)

        def find_one(self, filt, *args, **kwargs):
            for d in self._docs:
                match = True
                for k, v in filt.items():
                    if d.get(k) != v:
                        match = False
                        break
                if match:
                    return d
            return None

        def insert_one(self, doc):
            # mimic pymongo InsertOneResult by returning the doc
            self._docs.append(dict(doc))
            class R:
                pass
            return R()

        def update_one(self, filt, update):
            for d in self._docs:
                match = True
                for k, v in filt.items():
                    if d.get(k) != v:
                        match = False
                        break
                if match:
                    # apply $set
                    for k, v in update.get('$set', {}).items():
                        d[k] = v
                    class R:
                        modified_count = 1
                    return R()
            class R:
                modified_count = 0
            return R()

        def delete_one(self, filt):
            for i, d in enumerate(self._docs):
                match = True
                for k, v in filt.items():
                    if d.get(k) != v:
                        match = False
                        break
                if match:
                    del self._docs[i]
                    class R:
                        deleted_count = 1
                    return R()
            class R:
                deleted_count = 0
            return R()

    class FakeDB:
        def __init__(self):
            self.cities = FakeCollection()

    fake_db = FakeDB()

    # pre-populate fake DB
    fake_docs = [
        {"name": "Tokyo", "country": "Japan", "population": 14000000},
        {"name": "Osaka", "country": "Japan", "population": 2700000},
    ]
    for d in fake_docs:
        fake_db.cities.insert_one(d)

    # monkeypatch the module-level db used by data.cities
    monkeypatch.setattr(dc, 'db', fake_db)

    all_cities = dc.get_all_cities()
    assert isinstance(all_cities, list)
    assert len(all_cities) == 2
    names = {c['name'] for c in all_cities}
    assert names == {"Tokyo", "Osaka"}


def test_update_city_returns_false_when_not_found(monkeypatch):
    """Ensure update_city returns False when no document matches."""

    class FakeCollection2:
        def __init__(self):
            self._docs = []

        def find(self, *a, **k):
            return iter(self._docs)

        def find_one(self, filt, *a, **k):
            return None

        def insert_one(self, doc):
            self._docs.append(dict(doc))
            class R:
                pass
            return R()

        def update_one(self, filt, update):
            class R:
                modified_count = 0
            return R()

        def delete_one(self, filt):
            class R:
                deleted_count = 0
            return R()

    class FakeDB2:
        def __init__(self):
            self.cities = FakeCollection2()

    fake_db2 = FakeDB2()
    monkeypatch.setattr(dc, 'db', fake_db2)

    # attempt to update a non-existent city
    success = dc.update_city('Nonexistent', {'population': 123})
    assert success is False


def test_update_city_returns_false_when_not_found(monkeypatch):
    """Ensure update_city returns False when no document matches."""

    class FakeCollection2:
        def __init__(self):
            self._docs = []

        def find(self, *a, **k):
            return iter(self._docs)

        def find_one(self, filt, *a, **k):
            return None

        def insert_one(self, doc):
            self._docs.append(dict(doc))
            class R:
                pass
            return R()

        def update_one(self, filt, update):
            class R:
                modified_count = 0
            return R()

        def delete_one(self, filt):
            class R:
                deleted_count = 0
            return R()

    class FakeDB2:
        def __init__(self):
            self.cities = FakeCollection2()

    fake_db2 = FakeDB2()
    monkeypatch.setattr(dc, 'db', fake_db2)

    # attempt to update a non-existent city
    success = dc.update_city('Nonexistent', {'population': 123})
    assert success is False
