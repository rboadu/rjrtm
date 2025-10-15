"""
Data access layer for the 'states' collection in MongoDB.
"""

import data.db_connect as dbc

STATES_COLL = "states"

def create_state(doc: dict):
    dbc.connect_db()
    return dbc.client[dbc.SE_DB][STATES_COLL].insert_one(doc).inserted_id


def read_state_by_code(code: str):
    dbc.connect_db()
    return dbc.client[dbc.SE_DB][STATES_COLL].find_one({"code": code})


def read_all_states():
    dbc.connect_db()
    return list(dbc.client[dbc.SE_DB][STATES_COLL].find())
