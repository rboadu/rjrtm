"""
Data access layer for the 'countries' collection in MongoDB.
"""
import data.db_connect as dbc
import data.cache as cache

COUNTRIES_COLL = "countries"


def create_country(doc: dict):
    dbc.connect_db()
    # Prevent duplicate country names (case-insensitive)
    existing = dbc.client[dbc.SE_DB][COUNTRIES_COLL].find_one(
        {"name": {"$regex": f"^{doc['name']}$", "$options": "i"}}
    )
    if existing:
        raise ValueError(f"Country '{doc['name']}' already exists")
    res = dbc.client[dbc.SE_DB][COUNTRIES_COLL].insert_one(doc).inserted_id
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
        delete_state(s["code"])
    result = dbc.client[dbc.SE_DB][COUNTRIES_COLL].delete_one({"name": name})
    if result.deleted_count > 0:
        cache.invalidate('countries:all')
    return result.deleted_count


def read_country_by_name(name: str):
    dbc.connect_db()
    return dbc.client[dbc.SE_DB][COUNTRIES_COLL].find_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}}
    )


def read_all_countries():
    cached = cache.get('countries:all')
    if cached is not None:
        return cached
    dbc.connect_db()
    countries = list(dbc.client[dbc.SE_DB][COUNTRIES_COLL].find())
    for c in countries:
        from data.db_connect import convert_mongo_id
        convert_mongo_id(c)
    cache.set('countries:all', countries)
    return countries


def search_countries_by_name(user_input: str):
    dbc.connect_db()
    results = list(dbc.client[dbc.SE_DB][COUNTRIES_COLL].find(
        {"name": {"$regex": user_input, "$options": "i"}}
    ))
    for c in results:
        from data.db_connect import convert_mongo_id
        convert_mongo_id(c)
    return results