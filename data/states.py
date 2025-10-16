"""
Data access layer for the 'states' collection in MongoDB.
"""

import data.db_connect as dbc

STATES_COLL = "states"

def create_state(doc: dict):
    """
    Creates a new state document in MongoDB.
    """ 

    dbc.connect_db()
    return dbc.client[dbc.SE_DB][STATES_COLL].insert_one(doc).inserted_id


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
    dbc.connect_db()
    return list(dbc.client[dbc.SE_DB][STATES_COLL].find())

def update_state(code: str, update_all_fields: dict):
    """
    Updates a state document by its code.
    """
    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][STATES_COLL].update_one(
        {"code": code},
        {"$set": update_all_fields}
    )
    return result.modified_count

def delete_state(code: str):
    """
    Deletes a state document by its code.
    """
    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][STATES_COLL].delete_one({"code": code})
    return result.deleted_count
