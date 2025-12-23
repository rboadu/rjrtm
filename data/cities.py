"""
Data access layer for the 'cities' collection in MongoDB.
"""
import data.db_connect as dbc
import data.cache as cache
from data.db_connect import convert_mongo_id

CITIES_COLL = "cities"

def get_all_cities():
    """Return a list of all cities."""
    cached = cache.get('cities:all')
    if cached is not None:
        return cached
    
    dbc.connect_db()
    cities = list(dbc.client[dbc.SE_DB][CITIES_COLL].find())
    for city in cities:
        convert_mongo_id(city)
    
    cache.set('cities:all', cities)
    return cities


def get_city_by_name(name):
    """Find first city by name (may not be unique)."""
    dbc.connect_db()
    city = dbc.client[dbc.SE_DB][CITIES_COLL].find_one({"name": name})
    if city:
        convert_mongo_id(city)
    return city


def get_city_by_name_and_country(name, country):
    """Find a specific city by name AND country."""
    dbc.connect_db()
    city = dbc.client[dbc.SE_DB][CITIES_COLL].find_one({"name": name, "country": country})
    if city:
        convert_mongo_id(city)
    return city


def add_city(city):
    """
    Add a new city document.

    Raises:
        ValueError: if city already exists (same name + country)
    """
    dbc.connect_db()
    name = city.get("name")
    country = city.get("country")

    if not name or not country:
        raise ValueError("City must include name and country")

    # DUPLICATE CHECK
    existing = dbc.client[dbc.SE_DB][CITIES_COLL].find_one({"name": name, "country": country})
    if existing:
        raise ValueError("City already exists")

    # Insert
    dbc.client[dbc.SE_DB][CITIES_COLL].insert_one(city)
    
    # Invalidate cache
    cache.invalidate('cities:all')

    # Re-fetch so _id is converted properly
    saved = get_city_by_name_and_country(name, country)
    return saved


def update_city(name, country, updates):
    """Update a city by name and country."""
    if not updates:
        return False

    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][CITIES_COLL].update_one(
        {"name": name, "country": country},
        {"$set": updates}
    )
    
    if result.matched_count > 0:
        cache.invalidate('cities:all')
    
    return result.matched_count > 0


def delete_city(name, country):
    """Delete a city by name and country."""
    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][CITIES_COLL].delete_one({"name": name, "country": country})
    
    if result.deleted_count > 0:
        cache.invalidate('cities:all')
    
    return result.deleted_count > 0