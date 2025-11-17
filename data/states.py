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
