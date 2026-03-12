"""
Data access layer for the 'cities' collection in MongoDB.
"""
import data.db_connect as dbc
import data.cache as cache
from data.db_connect import convert_mongo_id
from data.countries import read_country_by_name
from data.states import read_state_by_code_and_country
import requests

CITIES_COLL = "cities"
COUNTRY_ALIASES = {
    "USA": "United States",
    "US": "United States",
    "UK": "United Kingdom",
    "UAE": "United Arab Emirates"
}


def get_all_cities():
    cached = cache.get('cities:all')
    if cached is not None:
        return cached
    dbc.connect_db()
    cities = list(dbc.client[dbc.SE_DB][CITIES_COLL].find())
    for city in cities:
        city.pop(dbc.MONGO_ID, None)
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

def geocode_city(name, state, country):
    """
    Use OpenStreetMap Nominatim to get lat/lng for a city.
    """
    country = COUNTRY_ALIASES.get(country, country)
    query = f"{name}, {state}, {country}"
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "geo-project"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if data:
            lat = float(data[0]["lat"])
            lng = float(data[0]["lon"])
            return lat, lng

    except Exception as e:
        print("Geocoding error:", e)

    return None, None

def add_city(city):
    """
    Add a new city. Validates that the state and country exist.
    """
    dbc.connect_db()
    name = city.get("name")
    state_code = city.get("state")
    country_name = city.get("country")

    # Validate required fields
    if not name or not state_code or not country_name:
        raise ValueError("City must include name, state, and country")

    # Validate country exists
    country = read_country_by_name(country_name)
    if not country:
        raise ValueError(f"Country '{country_name}' does not exist")

    # Validate state exists
    state = read_state_by_code_and_country(state_code, country_name)
    if not state:
        raise ValueError(f"State '{state_code}' does not exist")

    # Prevent duplicate cities
    existing = dbc.client[dbc.SE_DB][CITIES_COLL].find_one({
        "name": name,
        "state": state_code,
        "country": country_name
    })
    if existing:
        raise ValueError(f"City '{name}' in '{state_code}, {country_name}' already exists")
    
    lat, lng = geocode_city(name, state_code, country_name)
    if lat is not None and lng is not None:
        city["lat"] = lat
        city["lng"] = lng

    # Insert city
    dbc.client[dbc.SE_DB][CITIES_COLL].insert_one(city)
    cache.invalidate('cities:all')

    # Return saved city
    saved = dbc.client[dbc.SE_DB][CITIES_COLL].find_one({
        "name": name,
        "state": state_code,
        "country": country_name
    })
    convert_mongo_id(saved)
    saved.pop("_id", None)  # ← only change
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


def delete_cities_by_state(code, country):
    dbc.connect_db()
    dbc.client[dbc.SE_DB][CITIES_COLL].delete_many({
        "state": code,
        "country": country
    })
    cache.invalidate('cities:all')