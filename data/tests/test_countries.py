import re
import data.countries as dc
import data.states as ds
import data.db_connect as dbc


class FakeCollection(list):
    def insert_one(self, doc):
        doc.setdefault("_id", len(self) + 1)
        self.append(doc)
        return type("FakeResult", (), {"inserted_id": len(self)})()

    def find_one(self, filt):
        for doc in self:
            for key, val in filt.items():
                if isinstance(val, dict) and "$regex" in val:
                    pattern = re.compile(val["$regex"], re.IGNORECASE if val.get("$options") == "i" else 0)
                    if not pattern.fullmatch(doc.get(key, "")):
                        break
                else:
                    if doc.get(key) != val:
                        break
            else:
                return doc
        return None

    def find(self, filt=None):
        if filt is None:
            return list(self)
        results = []
        for doc in self:
            for key, val in filt.items():
                if isinstance(val, dict) and "$regex" in val:
                    pattern = re.compile(val["$regex"], re.IGNORECASE if val.get("$options") == "i" else 0)
                    if not pattern.search(doc.get(key, "")):
                        break
                else:
                    if doc.get(key) != val:
                        break
            else:
                results.append(doc)
        return results

    def delete_one(self, filt):
        for i, doc in enumerate(self):
            match = all(doc.get(k) == v for k, v in filt.items())
            if match:
                self.pop(i)
                return type("FakeResult", (), {"deleted_count": 1})()
        return type("FakeResult", (), {"deleted_count": 0})()


class FakeClient(dict):
    def __getitem__(self, name):
        if name not in self:
            self[name] = {dc.COUNTRIES_COLL: FakeCollection()}
        return super().__getitem__(name)


def _setup(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(dc.dbc, "client", fake_client)
    monkeypatch.setattr(dc.dbc, "connect_db", lambda: None)
    monkeypatch.setattr(dc.cache, "get", lambda key: None)
    monkeypatch.setattr(dc.cache, "set", lambda key, val: None)
    monkeypatch.setattr(dc.cache, "invalidate", lambda key: None)
    return fake_client


def test_create_and_read(monkeypatch):
    _setup(monkeypatch)

    country = {"code": "US", "name": "United States"}
    _id = dc.create_country(country)
    assert _id is not None

    rec = dc.read_country_by_name("United States")
    assert rec["name"] == "United States"

    all_countries = dc.read_all_countries()
    assert len(all_countries) == 1
    assert all_countries[0]["code"] == "US"


def test_duplicate_country_raises(monkeypatch):
    _setup(monkeypatch)

    dc.create_country({"name": "France"})
    try:
        dc.create_country({"name": "France"})
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "already exists" in str(e)


def test_read_country_not_found(monkeypatch):
    _setup(monkeypatch)
    result = dc.read_country_by_name("Nonexistent")
    assert result is None


def test_read_all_countries_empty(monkeypatch):
    _setup(monkeypatch)
    result = dc.read_all_countries()
    assert result == []


def test_read_all_countries_no_id_field(monkeypatch):
    _setup(monkeypatch)
    dc.create_country({"name": "Germany"})
    all_countries = dc.read_all_countries()
    assert "_id" not in all_countries[0]


def test_search_countries_by_name(monkeypatch):
    _setup(monkeypatch)

    dc.create_country({"name": "United States"})
    dc.create_country({"name": "United Kingdom"})
    dc.create_country({"name": "France"})

    results = dc.search_countries_by_name("United")
    assert len(results) == 2
    names = [r["name"] for r in results]
    assert "United States" in names
    assert "United Kingdom" in names


def test_delete_country(monkeypatch):
    _setup(monkeypatch)
    monkeypatch.setattr(ds, "read_states_by_country", lambda name: [])

    dc.create_country({"name": "Spain"})
    deleted = dc.delete_country_by_name("Spain")
    assert deleted == 1

    result = dc.read_country_by_name("Spain")
    assert result is None


def test_delete_nonexistent_country(monkeypatch):
    _setup(monkeypatch)
    monkeypatch.setattr(ds, "read_states_by_country", lambda name: [])

    deleted = dc.delete_country_by_name("Atlantis")
    assert not deleted