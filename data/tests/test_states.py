import data.states as ds

class FakeCollection(list):
    def insert_one(self, doc):
        self.append(doc)
        return type("FakeResult", (), {"inserted_id": len(self)})

    def find_one(self, filt):
        for doc in self:
            if doc.get("code") == filt.get("code"):
                return doc
        return None

    def find(self, filt=None):
        if filt is None:
            return self
        # Filter by country if provided
        return [doc for doc in self if doc.get("country") == filt.get("country")]


class FakeClient(dict):
    def __getitem__(self, name):
        if name not in self:
            self[name] = {ds.STATES_COLL: FakeCollection()}
        return super().__getitem__(name)


def test_create_and_read(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(ds.dbc, "client", fake_client)
    monkeypatch.setattr(ds.dbc, "connect_db", lambda: None)

    state = {"code": "NY", "name": "New York"}
    _id = ds.create_state(state)
    assert _id == 1

    rec = ds.read_state_by_code("NY")
    assert rec["name"] == "New York"

    all_states = ds.read_all_states()
    assert len(all_states) == 1
    assert all_states[0]["code"] == "NY"


def test_read_states_by_country(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(ds.dbc, "client", fake_client)
    monkeypatch.setattr(ds.dbc, "connect_db", lambda: None)

    # Create multiple states for different countries
    states = [
        {"code": "TX", "name": "Texas", "country": "USA"},
        {"code": "CA", "name": "California", "country": "USA"},
        {"code": "ON", "name": "Ontario", "country": "Canada"},
    ]
    for state in states:
        ds.create_state(state)

    # Test reading states by country
    usa_states = ds.read_states_by_country("USA")
    assert len(usa_states) == 2
    assert usa_states[0]["code"] == "TX"
    assert usa_states[1]["code"] == "CA"

    canada_states = ds.read_states_by_country("Canada")
    assert len(canada_states) == 1
    assert canada_states[0]["code"] == "ON"

    # Test non-existent country
    other_states = ds.read_states_by_country("NONEXISTENT")
    assert len(other_states) == 0
