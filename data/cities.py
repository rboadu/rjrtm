import logging
from data.db_connect import connect_db, SE_DB, convert_mongo_id

# Initialize logger (safe at import time)
logger = logging.getLogger(__name__)

# ⚠️ DO NOT perform any DB queries or log DB state here.
client = connect_db()
db = client[SE_DB]


def get_all_cities():
    """Return a list of all cities."""
    logger.debug("Fetching all cities from DB.")
    
    cities = list(db.cities.find())
    logger.debug("Fetched %d cities.", len(cities))

    for city in cities:
        convert_mongo_id(city)

    return cities


def get_city_by_name(name):
    """Find first city by name (may not be unique)."""
    logger.debug("Looking up city by name: %s", name)
    
    city = db.cities.find_one({"name": name})

    if city:
        logger.debug("City found with _id=%s", city.get("_id"))
        convert_mongo_id(city)
    else:
        logger.debug("No city found with name=%s", name)

    return city


def get_city_by_name_and_country(name, country):
    """Find a specific city by name AND country."""
    logger.debug("Looking up city by name=%s, country=%s", name, country)

    city = db.cities.find_one({"name": name, "country": country})

    if city:
        logger.debug("City located: _id=%s", city.get("_id"))
        convert_mongo_id(city)
    else:
        logger.debug(
            "No city found matching name=%s and country=%s",
            name, country
        )

    return city


def add_city(city):
    """Add a new city document. Raises ValueError if city already exists."""
    name = city.get("name")
    country = city.get("country")

    logger.debug("Attempting to add city name=%s, country=%s", name, country)

    existing = get_city_by_name_and_country(name, country)
    if existing:
        logger.warning(
            "City already exists: name=%s, country=%s. Add aborted.",
            name, country
        )
        raise ValueError(
            f"City '{name}' in '{country}' already exists"
        )

    result = db.cities.insert_one(city)
    city["_id"] = str(result.inserted_id)

    logger.debug("City added successfully with _id=%s", result.inserted_id)

    return city


def update_city(name, country, updated_city):
    """Update a city's information by name and country."""
    logger.debug(
        "Updating city name=%s, country=%s with fields=%s",
        name, country, list(updated_city.keys())
    )

    result = db.cities.update_one(
        {"name": name, "country": country},
        {"$set": updated_city}
    )

    if result.modified_count > 0:
        logger.debug("City update successful.")
        return True
    else:
        logger.debug("City update failed (no matching doc or no changes).")
        return False


def delete_city(name, country):
    """Delete a specific city by name AND country."""
    logger.debug("Deleting city name=%s, country=%s", name, country)

    result = db.cities.delete_one({"name": name, "country": country})

    if result.deleted_count > 0:
        logger.debug("City deleted successfully.")
        return True
    else:
        logger.debug("City delete failed (no matching doc).")
        return False


def reset_cities():
    """Clear all cities from the database (mock or real)."""
    logger.warning("Resetting all cities — deleting all documents in 'cities' collection.")

    result = db.cities.delete_many({})
    logger.debug("Deleted %d city documents.", result.deleted_count)
