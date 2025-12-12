"""
Data access layer for the 'states' collection in MongoDB.
"""

import data.db_connect as dbc
import data.cache as cache

STATES_COLL = "states"

def create_state(doc: dict):
    """
    Creates a new state document in MongoDB.
    """ 

    dbc.connect_db()
    res = dbc.client[dbc.SE_DB][STATES_COLL].insert_one(doc).inserted_id
    # invalidate cached states list
    cache.invalidate('states:all')
    return res


def read_state_by_code(code: str):
    """
    Reads a state document by its code.
    """
    dbc.connect_db()
    return dbc.client[dbc.SE_DB][STATES_COLL].find_one({"code": code})


def read_all_states():
    """
    Reads all of the state documents from MongoDB.
    """
    # Try cache first
    cached = cache.get('states:all')
    if cached is not None:
        return cached
    dbc.connect_db()
    docs = list(dbc.client[dbc.SE_DB][STATES_COLL].find())
    cache.set('states:all', docs)
    return docs

def update_state(code: str, update_all_fields: dict):
    """
    Updates a state document by its code.
    """
    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][STATES_COLL].update_one(
        {"code": code},
        {"$set": update_all_fields}
    )
    # invalidate cache on update
    cache.invalidate('states:all')
    return result.modified_count

def delete_state(code: str):
    """
    Deletes a state document by its code.
    """
    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][STATES_COLL].delete_one({"code": code})
    # invalidate cache on delete
    cache.invalidate('states:all')
    return result.deleted_count


def create_states_bulk(docs: list):
    """
    Insert multiple state documents in one operation.

    Returns a list of inserted id strings.
    """
    if not isinstance(docs, list):
        raise TypeError("docs must be a list of dicts")

    # ensure all items are dict-like
    valid_docs = [d for d in docs if isinstance(d, dict)]
    if not valid_docs:
        return []

    dbc.connect_db()
    res = dbc.client[dbc.SE_DB][STATES_COLL].insert_many(valid_docs)
    # invalidate cached states list once after bulk insert
    cache.invalidate('states:all')
    # return stringified ids for readability
    return [str(i) for i in res.inserted_ids]


def read_states_by_country(country: str):
    """
    Reads all state documents for a given country.
    """
    dbc.connect_db()
    return list(dbc.client[dbc.SE_DB][STATES_COLL].find({"country": country}))
