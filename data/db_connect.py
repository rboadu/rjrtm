"""
All interaction with MongoDB should be through this file!
We may be required to use a new database at any point.
"""
import os

import pymongo as pm

LOCAL = "0"
CLOUD = "1"

SE_DB = 'seDB'

client = None

MONGO_ID = '_id'


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        print('Setting client because it is None.')
        if os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD:
            password = os.environ.get('MONGO_PASSWD')
            if not password:
                raise ValueError('You must set your password '
                                 + 'to use Mongo in the cloud.')
            print('Connecting to Mongo in the cloud.')
            client = pm.MongoClient(f'mongodb+srv://gcallah:{password}'
                                    + '@koukoumongo1.yud9b.mongodb.net/'
                                    + '?retryWrites=true&w=majority')
        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient()
    return client


def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        # Convert mongo ID to a string so it works as JSON
        doc[MONGO_ID] = str(doc[MONGO_ID])


def create(collection, doc, db=SE_DB):
    """
    Insert a single doc into collection.
    """
    print(f'{db=}')
    return client[db][collection].insert_one(doc)


def read_one(collection, filt, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    for doc in client[db][collection].find(filt):
        convert_mongo_id(doc)
        return doc

def read_many(collection, filt, db=SE_DB, no_id=True) -> list:
    """
    Find multiple documents with a filter and return as a list.
    """
    res = []
    for doc in client[db][collection].find(filt):
        if not no_id:
            convert_mongo_id(doc)
        else:
            del doc[MONGO_ID]
        res.append(doc)
    return res

def delete(collection: str, filt: dict, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    """
    print(f'{filt=}')
    del_result = client[db][collection].delete_one(filt)
    return del_result.deleted_count


def update(collection, filters, update_dict, db=SE_DB):
    return client[db][collection].update_one(filters, {'$set': update_dict})


def read(collection, db=SE_DB, no_id=True) -> list:
    """
    Returns a list from the db.
    """
    ret = []
    for doc in client[db][collection].find():
        if no_id:
            del doc[MONGO_ID]
        else:
            convert_mongo_id(doc)
        ret.append(doc)
    return ret


def read_dict(collection, key, db=SE_DB, no_id=True) -> dict:
    recs = read(collection, db=db, no_id=no_id)
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict


def fetch_all_as_dict(key, collection, db=SE_DB):
    ret = {}
    for doc in client[db][collection].find():
        del doc[MONGO_ID]
        ret[doc[key]] = doc
    return ret

from __future__ import annotations
from typing import Optional
import logging
from urllib.parse import urlparse, urlunparse

"""
Helper utilities for connection handling. These are additive and do not alter
existing behavior or import-time side effects.
"""

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-scoped logger (no handlers/config set here)."""
    return logging.getLogger(name or __name__)

_SUPPORTED = {"mongodb", "postgres", "postgresql", "mysql", "sqlite"}

def is_supported_scheme(url: Optional[str]) -> bool:
    """True if URL has a recognized scheme (mongodb/postgres/mysql/sqlite)."""
    if not url:
        return False
    scheme = urlparse(url).scheme.lower()
    return scheme in _SUPPORTED

def normalize_url(url: str) -> str:
    """
    Normalize trivial variants (e.g., 'postgres' -> 'postgresql') without
    changing credentials/host/db. No network calls.
    """
    p = urlparse(url)
    scheme = "postgresql" if p.scheme.lower() == "postgres" else p.scheme
    return urlunparse((scheme, p.netloc, p.path, p.params, p.query, p.fragment))

def safe_preview(url: Optional[str]) -> str:
    """
    Return a redacted preview of a DB URL for logging: user shown, password hidden.
    Examples:
      mongodb://user:****@localhost:27017/mydb
      postgresql://user@db.example.com:5432/app
    """
    if not url:
        return "(no url)"
    p = urlparse(url)
    # redact password if present
    if p.username:
        cred = p.username + (":****" if p.password else "")
        netloc = f"{cred}@{p.hostname or ''}"
        if p.port:
            netloc += f":{p.port}"
    else:
        netloc = p.netloc
    return urlunparse((p.scheme, netloc, p.path, p.params, p.query, p.fragment))
