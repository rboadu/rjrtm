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
    """Find a city by name."""
    city = db.cities.find_one({"name": name})
    if city:
        convert_mongo_id(city)
    return city

def add_city(city):
    """Add a new city document."""
    result = db.cities.insert_one(city)
    # Attach a string version of the Mongo _id for JSON serialization
    city["_id"] = str(result.inserted_id)
    return city

def update_city(name, updated_city):
    """Update a city's information."""
    result = db.cities.update_one({"name": name}, {"$set": updated_city})
    return result.modified_count > 0

def delete_city(name):
    """Delete a city by name."""
    result = db.cities.delete_one({"name": name})
    return result.deleted_count > 0
