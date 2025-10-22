from data.db_connect import connect_db, SE_DB

client = connect_db()
db = client[SE_DB]

def get_all_cities():
    """Return a list of all cities."""
    cities = list(db.cities.find({}, {"_id": 0}))
    return cities

def get_city_by_name(name):
    """Find a city by name."""
    city = db.cities.find_one({"name": name}, {"_id": 0})
    return city

def add_city(city):
    """Add a new city document."""
    db.cities.insert_one(city)
    return city

def update_city(name, updated_city):
    """Update a city's information."""
    result = db.cities.update_one({"name": name}, {"$set": updated_city})
    return result.modified_count > 0

def delete_city(name):
    """Delete a city by name."""
    result = db.cities.delete_one({"name": name})
    return result.deleted_count > 0
