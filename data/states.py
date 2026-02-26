"""
Data access layer for the 'states' collection in MongoDB.
"""
import data.db_connect as dbc
import data.cache as cache
from data.countries import read_country_by_name

STATES_COLL = "states"


def create_state(doc: dict):
    """
    Creates a new state document in MongoDB.
    Ensures referenced country exists by name.
    State code must be letters only (e.g. NY, CA).
    """
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
    cache.invalidate('states:all')
    return res


def read_state_by_code(code: str):
    dbc.connect_db()
    return dbc.client[dbc.SE_DB][STATES_COLL].find_one({"code": code})


def read_all_states():
    cached = cache.get('states:all')
    if cached is not None:
        return cached
    dbc.connect_db()
    docs = list(dbc.client[dbc.SE_DB][STATES_COLL].find())
    for d in docs:
        from data.db_connect import convert_mongo_id
        convert_mongo_id(d)
    cache.set('states:all', docs)
    return docs


def update_state(code: str, update_all_fields: dict):
    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][STATES_COLL].update_one(
        {"code": code},
        {"$set": update_all_fields}
    )
    cache.invalidate('states:all')
    return result.modified_count


def delete_state(code: str):
    """
    Deletes state AND cascades delete to cities belonging to it.
    """
    from data.cities import delete_cities_by_state
    dbc.connect_db()
    delete_cities_by_state(code)
    result = dbc.client[dbc.SE_DB][STATES_COLL].delete_one({"code": code})
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
    return list(dbc.client[dbc.SE_DB][STATES_COLL].find({"country": country}))