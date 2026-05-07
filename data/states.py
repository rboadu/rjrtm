"""
Data access layer for the 'states' collection in MongoDB.
"""
import data.db_connect as dbc
import data.cache as cache
from data.countries import read_country_by_name
from data.db_connect import convert_mongo_id

STATES_COLL = "states"

def create_state(doc: dict):
    dbc.connect_db()
    country_name = doc.get("country")
    if not country_name:
        raise ValueError("State must include a country name")
    country = read_country_by_name(country_name)
    if not country:
        raise ValueError(f"Country '{country_name}' does not exist")
    code = doc.get("code", "")
    if not code.isalpha():
        raise ValueError("State code must contain letters only (e.g. NY, CA)")
    res = dbc.client[dbc.SE_DB][STATES_COLL].insert_one(doc).inserted_id
    doc.pop("_id", None)  # ← add this line
    cache.invalidate('states:all')
    return str(res)

def read_state_by_code_and_country(code: str, country: str):
    dbc.connect_db()
    doc = dbc.client[dbc.SE_DB][STATES_COLL].find_one({
        "code": code,
        "country": country
    })
    if doc:
        convert_mongo_id(doc)
    return doc

def read_all_states():
    cached = cache.get('states:all')
    if cached is not None:
        return cached
    dbc.connect_db()
    docs = list(dbc.client[dbc.SE_DB][STATES_COLL].find())
    for d in docs:
        d.pop(dbc.MONGO_ID, None)
    cache.set('states:all', docs)
    return docs

def update_state(code: str, country: str, update_all_fields: dict):
    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][STATES_COLL].update_one(
        {"code": code, "country": country},
        {"$set": update_all_fields}
    )
    cache.invalidate('states:all')
    return result.modified_count

def delete_state(code: str, country: str):
    from data.cities import delete_cities_by_state
    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][STATES_COLL].delete_one({
        "code": code,
        "country": country
    })
    delete_cities_by_state(code, country)
    cache.invalidate('states:all')
    return result.deleted_count

def create_states_bulk(docs: list):
    """
    Insert multiple states with validation.
    """
    if not isinstance(docs, list):
        raise TypeError("docs must be a list of dicts")
    valid_docs = []
    for d in docs:
        if not isinstance(d, dict):
            continue
        country_name = d.get("country")
        if not country_name:
            continue
        if not read_country_by_name(country_name):
            continue
        code = d.get("code", "")
        if not code.isalpha():
            continue
        valid_docs.append(d)
    if not valid_docs:
        return []
    dbc.connect_db()
    res = dbc.client[dbc.SE_DB][STATES_COLL].insert_many(valid_docs)
    cache.invalidate('states:all')
    return [str(i) for i in res.inserted_ids]

def read_states_by_country(country: str):
    dbc.connect_db()
    docs = list(dbc.client[dbc.SE_DB][STATES_COLL].find({"country": country}))
    for d in docs:
        convert_mongo_id(d)
    return docs