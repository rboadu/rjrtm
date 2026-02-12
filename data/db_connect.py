"""
All interaction with MongoDB should be through this file!
We may be required to use a new database at any point.
"""
import os

import pymongo as pm

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOCAL = "0"
CLOUD = "1"

SE_DB = 'seDB'

client = None

MONGO_ID = '_id'

MIN_ID_LEN = 4

user_nm = os.getenv('MONGO_USER_NM', 'datamixmaster')
cloud_svc = os.getenv('MONGO_HOST', 'datamixmaster.26rvk.mongodb.net')
passwd = os.environ.get("MONGO_PASSWD", '')
cloud_mdb = "mongodb+srv"
db_params = "retryWrites=false&w=majority"

# parameter names of mongo client settings
SERVER_API_PARAM = 'server_api'
CONN_TIMEOUT = 'connectTimeoutMS'
SOCK_TIMEOUT = 'socketTimeoutMS'
CONNECT = 'connect'
MAX_POOL_SIZE = 'maxPoolSize'


# Recommended Python Anywhere settings.
# We will use them eveywhere for now, until we determine some
# other site needs different settings.
PA_MONGO = os.getenv('PA_MONGO', True)
PA_SETTINGS = {
    CONN_TIMEOUT: os.getenv('MONGO_CONN_TIMEOUT', 30000),
    SOCK_TIMEOUT: os.getenv('MONGO_SOCK_TIMEOUT', None),
    CONNECT: os.getenv('MONGO_CONNECT', False),
    MAX_POOL_SIZE: os.getenv('MONGO_MAX_POOL_SIZE', 1),
}

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
            
            # Use environment variables for connection details
            user = os.getenv('MONGO_USER_NM', 'rboadu')
            host = os.getenv('MONGO_HOST', 'cluster0.thvwqrw.mongodb.net')
            app_name = os.getenv('MONGO_APP_NAME', 'Cluster0')
            
            connection_string = f'mongodb+srv://{user}:{password}@{host}/?appName={app_name}'
            
            # Apply PythonAnywhere settings if PA_MONGO is enabled
            if PA_MONGO:
                client = pm.MongoClient(connection_string, **PA_SETTINGS)
                print(f'Connected with PythonAnywhere settings: {PA_SETTINGS}')
            else:
                client = pm.MongoClient(connection_string)
                
            print(f'Connected to MongoDB at {host} as user {user}')
        else:
            print("Connecting to Mongo locally at mongodb://localhost:27017")
            client = pm.MongoClient("mongodb://localhost:27017",
                                    serverSelectionTimeoutMS=3000)

    return client



def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        # Convert mongo ID to a string so it works as JSON
        doc[MONGO_ID] = str(doc[MONGO_ID])


def ensure_connection(func):
    """Ensures that each call to DB has a connected client."""
    def wrapper(*args, **kwargs):
        connect_db()
        return func(*args, **kwargs)
    return wrapper


@ensure_connection
def create(collection, doc, db=SE_DB):
    """
    Insert a single doc into collection.
    """
    print(f'{db=}')
    return client[db][collection].insert_one(doc)


@ensure_connection
def read_one(collection, filt, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    for doc in client[db][collection].find(filt):
        convert_mongo_id(doc)
        return doc


@ensure_connection
def delete(collection: str, filt: dict, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    """
    print(f'{filt=}')
    del_result = client[db][collection].delete_one(filt)
    return del_result.deleted_count


@ensure_connection
def update(collection, filters, update_dict, db=SE_DB):
    return client[db][collection].update_one(filters, {'$set': update_dict})


@ensure_connection
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


@ensure_connection
def read_dict(collection, key, db=SE_DB, no_id=True) -> dict:
    recs = read(collection, db=db, no_id=no_id)
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict


@ensure_connection
def fetch_all_as_dict(key, collection, db=SE_DB):
    ret = {}
    for doc in client[db][collection].find():
        del doc[MONGO_ID]
        ret[doc[key]] = doc
    return ret
