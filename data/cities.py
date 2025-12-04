"""
Data access layer for the 'cities' collection in MongoDB.
Uses decorated helper functions to ensure each call has a valid DB connection.
Provides a simple in-memory cache for get_all_cities to reduce DB load.
"""

from typing import Any, Dict, List, Optional

from data.db_connect import (
    create,
    read_one,
    update,
    delete,
    read,
    SE_DB,
    convert_mongo_id,
)

COLLECTION = "cities"

# Simple in-memory cache of all cities.
# Invalidated on any write operation (create, update, delete).
_cities_cache: Optional[List[Dict[str, Any]]] = None


def _invalidate_cache() -> None:
    """Clear the in-memory cache of cities."""
    global _cities_cache
    _cities_cache = None


def get_all_cities() -> List[Dict[str, Any]]:
    """
    Return a list of all cities.

    Results are cached in memory until a write operation
    (add_city, update_city, delete_city) invalidates the cache.
    """
    global _cities_cache

    if _cities_cache is not None:
        return _cities_cache

    cities = read(COLLECTION, db=SE_DB, no_id=False)
    for city in cities:
        convert_mongo_id(city)

    _cities_cache = cities
    return cities


def get_city_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Find a city by its name, or return None if not found."""
    city = read_one(COLLECTION, {"name": name}, db=SE_DB)
    if city:
        convert_mongo_id(city)
    return city


def add_city(city: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new city document and return the created record."""
    result = create(COLLECTION, city, db=SE_DB)
    city["_id"] = str(result.inserted_id)
    _invalidate_cache()
    return city


def update_city(name: str, updated_city: Dict[str, Any]) -> bool:
    """
    Update a city's information.

    Returns True if a document was modified, False otherwise.
    """
    result = update(COLLECTION, {"name": name}, updated_city, db=SE_DB)
    modified = getattr(result, "modified_count", 0) > 0
    if modified:
        _invalidate_cache()
    return modified


def delete_city(name: str) -> bool:
    """
    Delete a city by name.

    Returns True if a document was deleted, False otherwise.
    """
    result = delete(COLLECTION, {"name": name}, db=SE_DB)
    # Depending on your delete helper, result may be a count or an object.
    deleted = False
    if isinstance(result, int):
        deleted = result > 0
    else:
        # e.g., result.deleted_count if using pymongo's DeleteResult
        deleted = getattr(result, "deleted_count", 0) > 0

    if deleted:
        _invalidate_cache()
    return deleted
