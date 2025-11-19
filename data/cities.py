"""
Data access layer for the 'cities' collection in MongoDB.
Uses decorated helper functions to ensure each call has a valid DB connection.
"""

from data.db_connect import create, read_one, update, delete, read, SE_DB, convert_mongo_id

COLLECTION = "cities"

def get_all_cities():
    """Return a list of all cities."""
    cities = read(COLLECTION, db=SE_DB, no_id=False)
    for city in cities:
        convert_mongo_id(city)
    return cities

def get_city_by_name(name):
    """Find a city by name."""
    city = read_one(COLLECTION, {"name": name}, db=SE_DB)
    if city:
        convert_mongo_id(city)
    return city

def add_city(city):
    """Add a new city document."""
    result = create(COLLECTION, city, db=SE_DB)
    city["_id"] = str(result.inserted_id)
    return city

def update_city(name, updated_city):
    """Update a city's information."""
    result = update(COLLECTION, {"name": name}, updated_city, db=SE_DB)
    return result.modified_count > 0

def delete_city(name):
    """Delete a city by name."""
    result = delete(COLLECTION, {"name": name}, db=SE_DB)
    return result > 0
