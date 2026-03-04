"""
Data access layer for the 'countries' collection in MongoDB.
"""
import data.db_connect as dbc
import data.cache as cache
from data.db_connect import convert_mongo_id

COUNTRIES_COLL = "countries"


def create_country(doc: dict):
    dbc.connect_db()
    existing = dbc.client[dbc.SE_DB][COUNTRIES_COLL].find_one(
        {"name": {"$regex": f"^{doc['name']}$", "$options": "i"}}
    )
    if existing:
        raise ValueError(f"Country '{doc['name']}' already exists")
    res = dbc.client[dbc.SE_DB][COUNTRIES_COLL].insert_one(doc).inserted_id
    doc.pop("_id", None)  # ← add this line
    cache.invalidate('countries:all')
    return res


def delete_country_by_name(name: str):
    """
    Delete country AND cascade delete states + cities.
    """
    from data.states import read_states_by_country, delete_state
    dbc.connect_db()
    states = read_states_by_country(name)
    for s in states:
        delete_state(s["code"], name)

    result = dbc.client[dbc.SE_DB][COUNTRIES_COLL].delete_one({"name": name})
    if result.deleted_count > 0:
        cache.invalidate('countries:all')
    return result.deleted_count


def read_country_by_name(name: str):
    dbc.connect_db()
    country = dbc.client[dbc.SE_DB][COUNTRIES_COLL].find_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}}
    )
    if country:
        country.pop(dbc.MONGO_ID, None)
    return country


def read_all_countries():
    cached = cache.get('countries:all')
    if cached is not None:
        return cached
    dbc.connect_db()
    countries = list(dbc.client[dbc.SE_DB][COUNTRIES_COLL].find())
    for c in countries:
        c.pop(dbc.MONGO_ID, None)
    cache.set('countries:all', countries)
    return countries


def search_countries_by_name(user_input: str):
    dbc.connect_db()
    results = list(dbc.client[dbc.SE_DB][COUNTRIES_COLL].find(
        {"name": {"$regex": user_input, "$options": "i"}}
    ))
    for c in results:
        c.pop(dbc.MONGO_ID, None)
    return results