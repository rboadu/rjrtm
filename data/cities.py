from data.db_connect import connect_db, SE_DB, convert_mongo_id

client = connect_db()
db = client[SE_DB]


def get_all_cities():
    """Return a list of all cities."""
    cities = list(db.cities.find())
    for city in cities:
        convert_mongo_id(city)
    return cities


def get_city_by_name(name):
    """Find first city by name (may not be unique)."""
    city = db.cities.find_one({"name": name})
    if city:
        convert_mongo_id(city)
    return city


def get_city_by_name_and_country(name, country):
    """Find a specific city by name AND country."""
    city = db.cities.find_one({"name": name, "country": country})
    if city:
        convert_mongo_id(city)
    return city


def add_city(city):
    """
    Add a new city document.

    Raises:
        ValueError: if city already exists (same name + country)
    """
    name = city.get("name")
    country = city.get("country")

    if not name or not country:
        raise ValueError("City must include name and country")

    # DUPLICATE CHECK
    existing = db.cities.find_one({"name": name, "country": country})
    if existing:
        raise ValueError("City already exists")

    # Insert
    db.cities.insert_one(city)

    # Re-fetch so _id is converted properly
    saved = get_city_by_name_and_country(name, country)
    return saved


def update_city(name, country, updates):
    """Update a city by name and country."""
    if not updates:
        return False

    result = db.cities.update_one(
        {"name": name, "country": country},
        {"$set": updates}
    )
    return result.matched_count > 0


def delete_city(name, country):
    """Delete a city by name and country."""
    result = db.cities.delete_one({"name": name, "country": country})
    return result.deleted_count > 0

def add_cities_bulk(cities):
    """
    Safely insert multiple cities.

    - Removes illegal fields
    - Deduplicates payload
    - Skips existing DB entries
    - Idempotent (safe to rerun)
    """
    if not cities or not isinstance(cities, list):
        return {"inserted": 0, "skipped": 0}

    cleaned = []
    seen = set()

    for city in cities:
        if not isinstance(city, dict):
            continue

        # Strip illegal fields
        city = {k: v for k, v in city.items() if k in ALLOWED_CITY_FIELDS}

        name = city.get("name")
        country = city.get("country")

        if not name or not country:
            continue

        key = (name.lower(), country.lower())
        if key in seen:
            continue  # duplicate in payload

        seen.add(key)
        cleaned.append(city)

    if not cleaned:
        return {"inserted": 0, "skipped": len(cities)}

    try:
        result = db.cities.insert_many(cleaned, ordered=False)
        return {
            "inserted": len(result.inserted_ids),
            "skipped": len(cities) - len(result.inserted_ids)
        }

    except BulkWriteError as e:
        inserted = e.details.get("nInserted", 0)
        return {
            "inserted": inserted,
            "skipped": len(cities) - inserted
        }
