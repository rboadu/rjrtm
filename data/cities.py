"""
Data access layer for the 'cities' collection in MongoDB.
"""
import data.db_connect as dbc
import data.cache as cache
from data.db_connect import convert_mongo_id
from data.countries import read_country_by_name

CITIES_COLL = "cities"


def get_all_cities():
    cached = cache.get('cities:all')
    if cached is not None:
        return cached
    dbc.connect_db()
    cities = list(dbc.client[dbc.SE_DB][CITIES_COLL].find())
    for city in cities:
        convert_mongo_id(city)
    cache.set('cities:all', cities)
    return cities


def get_city_by_name_and_country(name, country):
    dbc.connect_db()
    city = dbc.client[dbc.SE_DB][CITIES_COLL].find_one(
        {"name": name, "country": country}
    )
    if city:
        convert_mongo_id(city)
    return city


def get_city_by_name(name):
    dbc.connect_db()
    city = dbc.client[dbc.SE_DB][CITIES_COLL].find_one({"name": name})
    if city:
        convert_mongo_id(city)
    return city


def add_city(city):
    """
    Add a new city. Validates that the country exists by name.
    """
    dbc.connect_db()

    name = city.get("name")
    country_name = city.get("country")

    if not name or not country_name:
        raise ValueError("City must include name and country")

    country = read_country_by_name(country_name)
    if not country:
        raise ValueError(f"Country '{country_name}' does not exist")

    existing = dbc.client[dbc.SE_DB][CITIES_COLL].find_one({
        "name": name,
        "country": country_name
    })
    if existing:
        raise ValueError(f"City '{name}' in '{country_name}' already exists")

    dbc.client[dbc.SE_DB][CITIES_COLL].insert_one(city)
    cache.invalidate('cities:all')

    saved = dbc.client[dbc.SE_DB][CITIES_COLL].find_one({
        "name": name,
        "country": country_name
    })
    convert_mongo_id(saved)
    return saved


def update_city(name, country, updates):
    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][CITIES_COLL].update_one(
        {"name": name, "country": country},
        {"$set": updates}
    )
    if result.matched_count > 0:
        cache.invalidate('cities:all')
    return result.matched_count > 0


def delete_city(name, country):
    dbc.connect_db()
    result = dbc.client[dbc.SE_DB][CITIES_COLL].delete_one({
        "name": name,
        "country": country
    })
    if result.deleted_count > 0:
        cache.invalidate('cities:all')
    return result.deleted_count > 0


def delete_cities_by_state(state_code):
    """
    Cascade helper used when deleting states.
    """
    dbc.connect_db()
    dbc.client[dbc.SE_DB][CITIES_COLL].delete_many({"state": state_code})
    cache.invalidate('cities:all')