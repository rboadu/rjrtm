import data.states as ds
import data.cities as city_module
import data.db_connect as dbc
import pytest


class FakeCollection(list):
    def insert_one(self, doc):
        doc.setdefault("_id", len(self) + 1)
        self.append(doc)
        return type("FakeResult", (), {"inserted_id": len(self)})()

    def find_one(self, filt):
        for doc in self:
            if doc.get("code") == filt.get("code") and doc.get("country") == filt.get("country"):
                return doc
        return None

    def find(self, filt=None):
        if filt is None:
            return list(self)
        return [doc for doc in self if doc.get("country") == filt.get("country")]

    def delete_one(self, filt):
        for i, doc in enumerate(self):
            if doc.get("code") == filt.get("code") and doc.get("country") == filt.get("country"):
                self.pop(i)
                return type("FakeResult", (), {"deleted_count": 1})()
        return type("FakeResult", (), {"deleted_count": 0})()

    def update_one(self, filt, update):
        for doc in self:
            if doc.get("code") == filt.get("code") and doc.get("country") == filt.get("country"):
                doc.update(update.get("$set", {}))
                return type("FakeResult", (), {"modified_count": 1})()
        return type("FakeResult", (), {"modified_count": 0})()


class FakeClient(dict):
    def __getitem__(self, name):
        if name not in self:
            self[name] = {ds.STATES_COLL: FakeCollection()}
        return super().__getitem__(name)


def _setup(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(ds.dbc, "client", fake_client)
    monkeypatch.setattr(ds.dbc, "connect_db", lambda: None)
    monkeypatch.setattr(ds, "read_country_by_name", lambda name: {"name": name})
    monkeypatch.setattr(ds.cache, "get", lambda key: None)
    monkeypatch.setattr(ds.cache, "set", lambda key, val: None)
    monkeypatch.setattr(ds.cache, "invalidate", lambda key: None)
    return fake_client


def test_create_and_read(monkeypatch):
    _setup(monkeypatch)

    state = {"code": "NY", "name": "New York", "country": "USA"}
    _id = ds.create_state(state)
    assert _id is not None

    rec = ds.read_state_by_code_and_country("NY", "USA")
    assert rec["name"] == "New York"

    all_states = ds.read_all_states()
    assert len(all_states) == 1
    assert all_states[0]["code"] == "NY"


def test_read_all_states_no_id_field(monkeypatch):
    _setup(monkeypatch)

    ds.create_state({"code": "CA", "name": "California", "country": "USA"})
    all_states = ds.read_all_states()
    assert "_id" not in all_states[0]


def test_create_state_missing_country(monkeypatch):
    _setup(monkeypatch)
    monkeypatch.setattr(ds, "read_country_by_name", lambda name: None)

    with pytest.raises(ValueError, match="does not exist"):
        ds.create_state({"code": "NY", "name": "New York", "country": "Fakeland"})


def test_create_state_invalid_code(monkeypatch):
    _setup(monkeypatch)

    with pytest.raises(ValueError, match="letters only"):
        ds.create_state({"code": "N1", "name": "Bad State", "country": "USA"})


def test_read_state_not_found(monkeypatch):
    _setup(monkeypatch)
    result = ds.read_state_by_code_and_country("ZZ", "USA")
    assert result is None


def test_read_states_by_country(monkeypatch):
    _setup(monkeypatch)

    states = [
        {"code": "TX", "name": "Texas", "country": "USA"},
        {"code": "CA", "name": "California", "country": "USA"},
        {"code": "ON", "name": "Ontario", "country": "Canada"},
    ]
    for state in states:
        ds.create_state(state)

    usa_states = ds.read_states_by_country("USA")
    assert len(usa_states) == 2
    codes = [s["code"] for s in usa_states]
    assert "TX" in codes
    assert "CA" in codes

    canada_states = ds.read_states_by_country("Canada")
    assert len(canada_states) == 1
    assert canada_states[0]["code"] == "ON"

    other_states = ds.read_states_by_country("NONEXISTENT")
    assert len(other_states) == 0


def test_update_state(monkeypatch):
    _setup(monkeypatch)

    ds.create_state({"code": "TX", "name": "Texas", "country": "USA"})
    modified = ds.update_state("TX", "USA", {"name": "Updated Texas"})
    assert modified == 1


def test_delete_state(monkeypatch):
    _setup(monkeypatch)
    monkeypatch.setattr(city_module, "delete_cities_by_state", lambda code, country: None)

    ds.create_state({"code": "FL", "name": "Florida", "country": "USA"})
    deleted = ds.delete_state("FL", "USA")
    assert deleted == 1

    result = ds.read_state_by_code_and_country("FL", "USA")
    assert result is None