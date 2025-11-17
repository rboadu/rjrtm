from pymongo import MongoClient

client = MongoClient()
db = client['seDB']

states = [
    {'code': 'NY', 'name': 'New York', 'population': 20000000},
    {'code': 'CA', 'name': 'California', 'population': 39500000},
    {'code': 'TX', 'name': 'Texas', 'population': 29000000},
]

for s in states:
    db.states.update_one({'code': s['code']}, {'$set': s}, upsert=True)

print('Seeded states')
