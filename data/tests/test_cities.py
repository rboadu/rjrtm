import pytest
import data.cities as city_module
import data.db_connect as dbc
import re


class FakeDeleteResult:
    def __init__(self, count):
        self.deleted_count = count


class FakeUpdateResult:
    def __init__(self, matched):
        self.matched_count = matched


class FakeCollection(list):
    def insert_one(self, doc):
        doc.setdefault("_id", len(self) + 1)
        self.append(doc)
        return type("FakeResult", (), {"inserted_id": len(self)})()

    def find_one(self, filt):
        for doc in self:
            if self._matches(doc, filt):
                return doc
        return None

    def find(self, filt=None):
        if filt is None:
            return list(self)
        return [doc for doc in self if self._matches(doc, filt)]

    def update_one(self, filt, update):
        for doc in self:
            if self._matches(doc, filt):
                doc.update(update.get("$set", {}))
                return FakeUpdateResult(1)
        return FakeUpdateResult(0)

    def delete_one(self, filt):
        for i, doc in enumerate(self):
            if self._matches(doc, filt):
                self.pop(i)
                return FakeDeleteResult(1)
        return FakeDeleteResult(0)

    def _matches(self, doc, filt):
        for key, val in filt.items():
            if doc.get(key) != val:
                return False
        return True


class FakeClient(dict):
    def __getitem__(self, name):
        if name not in self:
            self[name] = {city_module.CITIES_COLL: FakeCollection()}
        return super().__getitem__(name)


def _setup(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(city_module.dbc, "client", fake_client)
    monkeypatch.setattr(city_module.dbc, "connect_db", lambda: None)
    monkeypatch.setattr(city_module, "read_country_by_name", lambda name: {"name": name})
    monkeypatch.setattr(city_module, "read_state_by_code_and_country", lambda code, country: {"code": code})
    monkeypatch.setattr(city_module.cache, "get", lambda key: None)
    monkeypatch.setattr(city_module.cache, "set", lambda key, val: None)
    monkeypatch.setattr(city_module.cache, "invalidate", lambda key: None)
    return fake_client


def test_add_and_get_city(monkeypatch):
    _setup(monkeypatch)

    city = {"name": "New York City", "state": "NY", "country": "USA", "population": 8000000}
    result = city_module.add_city(city)
    assert result["name"] == "New York City"

    fetched = city_module.get_city_by_name_and_country("New York City", "USA")
    assert fetched["name"] == "New York City"


def test_add_city_no_id_in_response(monkeypatch):
    _setup(monkeypatch)

    city = {"name": "Chicago", "state": "IL", "country": "USA", "population": 2700000}
    result = city_module.add_city(city)
    assert "_id" not in result


def test_add_city_missing_fields(monkeypatch):
    _setup(monkeypatch)

    with pytest.raises(ValueError, match="must include"):
        city_module.add_city({"name": "NoState", "country": "USA"})

    with pytest.raises(ValueError, match="must include"):
        city_module.add_city({"state": "NY", "country": "USA"})


def test_add_city_invalid_country(monkeypatch):
    _setup(monkeypatch)
    monkeypatch.setattr(city_module, "read_country_by_name", lambda name: None)

    with pytest.raises(ValueError, match="does not exist"):
        city_module.add_city({"name": "Ghost", "state": "NY", "country": "Fakeland"})


def test_add_city_invalid_state(monkeypatch):
    _setup(monkeypatch)
    monkeypatch.setattr(city_module, "read_state_by_code_and_country", lambda code, country: None)

    with pytest.raises(ValueError, match="does not exist"):
        city_module.add_city({"name": "Ghost", "state": "ZZ", "country": "USA"})


def test_add_duplicate_city(monkeypatch):
    _setup(monkeypatch)

    city = {"name": "Boston", "state": "MA", "country": "USA"}
    city_module.add_city(city)

    with pytest.raises(ValueError, match="already exists"):
        city_module.add_city({"name": "Boston", "state": "MA", "country": "USA"})


def test_get_all_cities_no_id(monkeypatch):
    _setup(monkeypatch)

    city_module.add_city({"name": "Seattle", "state": "WA", "country": "USA"})
    all_cities = city_module.get_all_cities()
    assert len(all_cities) == 1
    assert "_id" not in all_cities[0]


def test_update_city(monkeypatch):
    _setup(monkeypatch)

    city_module.add_city({"name": "Dallas", "state": "TX", "country": "USA", "population": 1000000})
    updated = city_module.update_city("Dallas", "USA", {"population": 1300000})
    assert updated is True


def test_delete_city(monkeypatch):
    _setup(monkeypatch)

    city_module.add_city({"name": "Austin", "state": "TX", "country": "USA"})
    deleted = city_module.delete_city("Austin", "USA")
    assert deleted is True

    result = city_module.get_city_by_name_and_country("Austin", "USA")
    assert result is None


def test_get_city_not_found(monkeypatch):
    _setup(monkeypatch)

    result = city_module.get_city_by_name_and_country("Nowhere", "USA")
    assert result is None