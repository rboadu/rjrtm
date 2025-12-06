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
    """Add a new city document. Raises ValueError if city already exists."""
    # Check if city already exists (by name AND country)
    existing = get_city_by_name_and_country(city.get("name"), city.get("country"))
    if existing:
        raise ValueError(f"City '{city.get('name')}' in '{city.get('country')}' already exists")
    
    result = db.cities.insert_one(city)
    city["_id"] = str(result.inserted_id)
    return city

def update_city(name, country, updated_city):
    """Update a city's information by name and country."""
    result = db.cities.update_one(
        {"name": name, "country": country}, 
        {"$set": updated_city}
    )
    return result.modified_count > 0

def delete_city(name, country):
    """Delete a specific city by name AND country."""
    result = db.cities.delete_many({"name": name, "country": country})
    return result.deleted_count > 0