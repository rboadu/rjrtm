"""
Data access layer for the 'countries' collection in MongoDB.
"""

import data.db_connect as dbc

COUNTRIES_COLL = "countries"

def create_country(doc: dict):
    """
    Insert a new country document into MongoDB.
    """
    dbc.connect_db()
    return dbc.client[dbc.SE_DB][COUNTRIES_COLL].insert_one(doc).inserted_id


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
    dbc.connect_db()
    return list(dbc.client[dbc.SE_DB][COUNTRIES_COLL].find())


''''
TODO:
create_country(doc: dict) -> inserted_id or raise DuplicateError
read_country_by_code(code: str) -> dict | None (convert _id to string)
read_all_countries(limit: int = 0, skip: int = 0, sort=None) -> list[dict]
update_country(code: str, update_dict: dict) -> bool (True if modified)
delete_country(code: str) -> int (deleted_count)

'''