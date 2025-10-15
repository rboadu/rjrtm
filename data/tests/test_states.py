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

    def find(self):
        return self


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
