import data.countries as dc

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
            self[name] = {dc.COUNTRIES_COLL: FakeCollection()}
        return super().__getitem__(name)


def test_create_and_read(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(dc.dbc, "client", fake_client)
    monkeypatch.setattr(dc.dbc, "connect_db", lambda: None)

    country = {"code": "US", "name": "United States"}
    _id = dc.create_country(country)
    assert _id == 1

    rec = dc.read_country_by_code("US")
    assert rec["name"] == "United States"

    all_countries = dc.read_all_countries()
    assert len(all_countries) == 1
    assert all_countries[0]["code"] == "US"
