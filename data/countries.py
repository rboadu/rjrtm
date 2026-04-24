"""
Data access layer for the 'countries' collection in MongoDB.
"""
import data.db_connect as dbc
import data.cache as cache
from data.db_connect import convert_mongo_id

COUNTRIES_COLL = "countries"


def _sanitize_country(doc: dict):
    if not doc:
        return doc
    doc.pop(dbc.MONGO_ID, None)
    doc.pop("password", None)
    return doc


def create_country(doc: dict):
    dbc.connect_db()
    country = dict(doc)
    if not country.get("password"):
        country.pop("password", None)
    existing = dbc.client[dbc.SE_DB][COUNTRIES_COLL].find_one(
        {"name": {"$regex": f"^{country['name']}$", "$options": "i"}}
    )
    if existing:
        raise ValueError(f"Country '{country['name']}' already exists")
    res = dbc.client[dbc.SE_DB][COUNTRIES_COLL].insert_one(country).inserted_id
    cache.invalidate('countries:all')
    return res


def update_country_by_name(name: str, updates: dict, password: str = None):
    dbc.connect_db()
    country = dbc.client[dbc.SE_DB][COUNTRIES_COLL].find_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}}
    )
    if not country:
        return 0

    stored_password = country.get("password")
    if stored_password and stored_password != password:
        raise PermissionError("Invalid country password")

    update_doc = dict(updates)
    update_doc.pop("password", None)
    update_doc.pop("_id", None)
    result = dbc.client[dbc.SE_DB][COUNTRIES_COLL].update_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}},
        {"$set": update_doc},
    )
    if result.matched_count > 0:
        cache.invalidate('countries:all')
    return result.matched_count


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
    return _sanitize_country(country)


def read_all_countries():
    cached = cache.get('countries:all')
    if cached is not None:
        return cached
    dbc.connect_db()
    countries = list(dbc.client[dbc.SE_DB][COUNTRIES_COLL].find())
    for c in countries:
        _sanitize_country(c)
    cache.set('countries:all', countries)
    return countries


def search_countries_by_name(user_input: str):
    dbc.connect_db()
    results = list(dbc.client[dbc.SE_DB][COUNTRIES_COLL].find(
        {"name": {"$regex": user_input, "$options": "i"}}
    ))
    for c in results:
        _sanitize_country(c)
    return results