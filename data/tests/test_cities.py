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

    # 🔒 DUPLICATE CHECK
    existing = db.cities.find_one({"name": name, "country": country})
    if existing:
        raise ValueError("City already exists")

    result = db.cities.insert_one(city)
    return result.inserted_id


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
