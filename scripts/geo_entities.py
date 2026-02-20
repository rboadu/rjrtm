import os
import argparse
import logging
from pymongo import MongoClient, errors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
# Set all database names
DB_NAME = os.getenv("DB_NAME", "rjrtm")

SAMPLE_COUNTRIES = [
    {"code": "US", "name": "United States"},
    {"code": "CA", "name": "Canada"},
    {"code": "GH", "name": "Ghana"},
]

SAMPLE_STATES = [
    {"code": "NY", "name": "New York", "country": "US"},
    {"code": "CA-ON", "name": "Ontario", "country": "CA"},
    {"code": "GH-EP", "name": "Eastern Region", "country": "GH"},
]

SAMPLE_CITIES = [
    {"name": "New York City", "country": "US", "population": 8419000},
    {"name": "Toronto", "country": "CA", "population": 2930000},
    {"name": "Kumasi", "country": "GH", "population": 2000000},
]


def get_db(uri=MONGO_URI, db_name=DB_NAME):
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    # trigger connection exception early
    client.admin.command("ping")
    return client[db_name]


def upsert_many(collection, key_fields, docs):
    for doc in docs:
        query = {k: doc[k] for k in key_fields}
        try:
            collection.update_one(query, {"$set": doc}, upsert=True)
            logger.info("Upserted %s into %s", query, collection.name)
        except errors.PyMongoError as e:
            logger.error("Failed to upsert %s: %s", query, e)


def insert_samples(db):
    countries = db.countries
    states = db.states
    cities = db.cities

    # create simple unique indexes to avoid duplicates (safe if exists)
    try:
        countries.create_index("code", unique=True)
        states.create_index([("code", 1), ("country", 1)], unique=True)
        cities.create_index([("name", 1), ("country", 1)], unique=True)
    except errors.PyMongoError:
        pass

    upsert_many(countries, ["code"], SAMPLE_COUNTRIES)
    upsert_many(states, ["code", "country"], SAMPLE_STATES)
    upsert_many(cities, ["name", "country"], SAMPLE_CITIES)
    logger.info("Sample data inserted/updated.")


def clear_collections(db):
    for name in ("countries", "states", "cities"):
        try:
            db[name].delete_many({})
            logger.info("Cleared collection: %s", name)
        except errors.PyMongoError as e:
            logger.error("Failed to clear %s: %s", name, e)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--insert", action="store_true", help="Insert sample data (upsert).")
    p.add_argument("--clear", action="store_true", help="Clear sample collections.")
    args = p.parse_args()

    try:
        db = get_db()
    except Exception as e:
        logger.error("Could not connect to MongoDB at %s: %s", MONGO_URI, e)
        return

    if args.clear:
        clear_collections(db)
    if args.insert:
        insert_samples(db)
    if not (args.insert or args.clear):
        p.print_help()


if __name__ == "__main__":
    main()