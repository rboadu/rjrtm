"""
Data access layer for the 'countries' collection in MongoDB.
"""

import data.db_connect as dbc
import data.cache as cache

COUNTRIES_COLL = "countries"

def create_country(doc: dict):
    """
    Insert a new country document into MongoDB.
    """
    dbc.connect_db()
    res = dbc.client[dbc.SE_DB][COUNTRIES_COLL].insert_one(doc).inserted_id
    # add to cache
    return res

def delete_country_by_code(code: str):
    """
    Delete a country by its code (e.g., 'US').
    """
    dbc.connect_db()
    if cache[code]:
        cache.invalidate(code)
    return dbc.client[dbc.SE_DB][COUNTRIES_COLL].delete_one({"code": code}).deleted_count

def read_country_by_code(code: str):
    """
    Retrieve a country by its code (e.g., 'US').
    """
    dbc.connect_db()
    return dbc.client[dbc.SE_DB][COUNTRIES_COLL].find_one({"code": code})


def read_all_countries():
    """
    Return a list of all countries.
    """
    cached = cache.get('countries:all')
    if cached is not None:
        return cached
    dbc.connect_db()
    countries = list(dbc.client[dbc.SE_DB][COUNTRIES_COLL].find())
    cache.set('countries:all', countries)
    return countries

def search_countries_by_name(user_input: str):
    """
    Search for countries by name, useful for search features.
    """
    dbc.connect_db()
    return list(dbc.client[dbc.SE_DB][COUNTRIES_COLL].find(
        {"name": {"$regex": user_input, "$options": "i"}}
    ))