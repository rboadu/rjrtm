import re
import data.countries as dc
import data.states as ds
import data.cities as city_module
import data.db_connect as dbc


class FakeDeleteResult:
    def __init__(self, count):
        self.deleted_count = count


class FakeCollection(list):
    def insert_one(self, doc):
        self.append(doc)
        return type("FakeResult", (), {"inserted_id": len(self)})()

    def find_one(self, filt):
        for doc in self:
            if self._matches(doc, filt):
                return doc
        return None

    def find(self, filt=None):
        if not filt:
            return list(self)
        return [doc for doc in self if self._matches(doc, filt)]

    def delete_one(self, filt):
        for i, doc in enumerate(self):
            if self._matches(doc, filt):
                self.pop(i)
                return FakeDeleteResult(1)
        return FakeDeleteResult(0)

    def delete_many(self, filt):
        to_remove = [doc for doc in self if self._matches(doc, filt)]
        for doc in to_remove:
            self.remove(doc)
        return FakeDeleteResult(len(to_remove))

    def _matches(self, doc, filt):
        for key, val in filt.items():
            if isinstance(val, dict) and "$regex" in val:
                pattern = re.compile(
                    val["$regex"],
                    re.IGNORECASE if val.get("$options") == "i" else 0
                )
                if not pattern.fullmatch(str(doc.get(key, ""))):
                    return False
            else:
                if doc.get(key) != val:
                    return False
        return True


def make_fake_client():
    countries_coll = FakeCollection()
    states_coll = FakeCollection()
    cities_coll = FakeCollection()
    fake_db = {
        dc.COUNTRIES_COLL: countries_coll,
        ds.STATES_COLL: states_coll,
        city_module.CITIES_COLL: cities_coll,
    }
    return {dbc.SE_DB: fake_db}


def test_delete_state_cascades_cities(monkeypatch):
    fake_client = make_fake_client()

    monkeypatch.setattr(ds.dbc, "client", fake_client)
    monkeypatch.setattr(ds.dbc, "connect_db", lambda: None)
    monkeypatch.setattr(city_module.dbc, "client", fake_client)
    monkeypatch.setattr(city_module.dbc, "connect_db", lambda: None)
    monkeypatch.setattr(ds, "read_country_by_name", lambda name: {"name": name})

    # create a state and two cities linked to it
    ds.create_state({"code": "NY", "name": "New York", "country": "USA"})
    fake_client[dbc.SE_DB][city_module.CITIES_COLL].insert_one(
        {"name": "New York City", "country": "USA", "state": "NY"}
    )
    fake_client[dbc.SE_DB][city_module.CITIES_COLL].insert_one(
        {"name": "Buffalo", "country": "USA", "state": "NY"}
    )

    assert len(fake_client[dbc.SE_DB][city_module.CITIES_COLL]) == 2

    ds.delete_state("NY")

    assert ds.read_state_by_code("NY") is None
    assert len(fake_client[dbc.SE_DB][city_module.CITIES_COLL]) == 0


def test_delete_country_cascades_states(monkeypatch):
    fake_client = make_fake_client()

    monkeypatch.setattr(dc.dbc, "client", fake_client)
    monkeypatch.setattr(dc.dbc, "connect_db", lambda: None)
    monkeypatch.setattr(ds.dbc, "client", fake_client)
    monkeypatch.setattr(ds.dbc, "connect_db", lambda: None)
    monkeypatch.setattr(city_module.dbc, "client", fake_client)
    monkeypatch.setattr(city_module.dbc, "connect_db", lambda: None)
    monkeypatch.setattr(ds, "read_country_by_name", lambda name: {"name": name})

    # create country and two states
    dc.create_country({"code": "US", "name": "USA"})
    ds.create_state({"code": "NY", "name": "New York", "country": "USA"})
    ds.create_state({"code": "CA", "name": "California", "country": "USA"})

    assert len(fake_client[dbc.SE_DB][ds.STATES_COLL]) == 2

    dc.delete_country_by_name("USA")

    assert dc.read_country_by_name("USA") is None
    assert len(fake_client[dbc.SE_DB][ds.STATES_COLL]) == 0