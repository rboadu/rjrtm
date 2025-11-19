from flask import Flask, jsonify, request
from flask_restx import Resource, Api, fields
from flask_cors import CORS
import data.states as ds
import data.cities as dc

app = Flask(__name__)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
MESSAGE = 'Message'
JOURNAL_EP = '/journal'
JOURNAL_RESP = 'journal'

# Models

state_model = api.model('State', {
    'code': fields.String(required=True, description='State code, e.g. NY'),
    'name': fields.String(required=True, description='State name, e.g. New York')
})

city_model = api.model('City', {
    'name': fields.String(required=True, description='City name'),
    'country': fields.String(required=True, description='Country where the city is located'),
    'population': fields.Integer(description='Population of the city')
})

journal_model = api.model('JournalEntry', {
    'entry': fields.String(required=True, description='Journal entry text')
})

# Endpoints

@api.route(HELLO_EP)
class HelloWorld(Resource):
    """Simple health check endpoint."""
    def get(self):
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """Return all available endpoints."""
    def get(self):
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(JOURNAL_EP)
class Journal(Resource):
    """A simple journal endpoint."""
    def get(self):
        return {JOURNAL_RESP: 'RJRTM Journal'}


@api.route('/journal/add')
class JournalAdd(Resource):
    @api.expect(journal_model)
    def post(self):
        data = api.payload
        entry = data.get('entry')
        if not entry:
            return {'error': 'Entry is required'}, 400
        return {'message': 'Entry added', 'entry': entry}, 201

# State Endpoints
@api.route('/states')
class States(Resource):
    @api.marshal_list_with(state_model)
    def get(self):
        """Return all states from the database."""
        states = ds.read_all_states()
        return states

    @api.expect(state_model)
    def post(self):
        """Add a new state."""
        data = api.payload
        ds.create_state(data)
        return {'message': 'State added successfully', 'state': data}, 201

@api.route('/states/<string:code>')

class StateByCode(Resource):
    def get(self, code):
        """Return a specific state by code."""
        state = ds.read_state_by_code(code)
        if state:
            # Marshal only the successful response to the state model
            return api.marshal(state, state_model), 200
        return {'error': 'State not found'}, 404

    @api.expect(state_model)
    def put(self, code):
        """Update a state by code."""
        data = api.payload
        updated = ds.update_state(code, data)
        if updated:
            return {'message': 'State updated', 'state': data}, 200
        return {'error': 'State not found'}, 404

    @api.expect(state_model)
    def patch(self, code):
        """Partially update a state by code."""
        data = api.payload or {}
        if not data:
            return {'error': 'No update fields provided'}, 400
        updated = ds.update_state(code, data)
        if updated:
            return {'message': 'State partially updated', 'state': data}, 200
        return {'error': 'State not found'}, 404

    def delete(self, code):
        """Delete a state by code."""
        deleted = ds.delete_state(code)
        if deleted:
            return {'message': 'State deleted'}, 200
        return {'error': 'State not found'}, 404

@api.route('/states/<string:code>/patch')
class StatePatch(Resource):
    @api.expect(state_model)
    def patch(self, code):
        updates = api.payload or {}
        if not updates:
            return {'error': 'No updates provided'}, 400
        updated = ds.update_state(code, updates)
        if updated:
            return {'message': 'State updated', 'state': updates}, 200
        return {'error': 'State not found'}, 404
    
def validate_city_payload(data, partial=False):
    allowed_fields = {"name", "country", "population"}
    required_fields = {"name", "country"}

    # Reject unknown fields
    for field in data:
        if field not in allowed_fields:
            return f"Unknown field: '{field}'", False

    # Require all fields unless partial=True (PATCH)
    if not partial:
        missing = required_fields - data.keys()
        if missing:
            return f"Missing required fields: {', '.join(missing)}", False

    # Type validation
    if "name" in data and not isinstance(data["name"], str):
        return "'name' must be a string", False

    if "country" in data and not isinstance(data["country"], str):
        return "'country' must be a string", False

    if "population" in data:
        pop = data["population"]
        if not isinstance(pop, int) or pop < 0:
            return "'population' must be a non-negative integer", False

    return "", True

@api.route('/cities')
class Cities(Resource):
    @api.marshal_list_with(city_model)
    @api.doc(params={
        'country': 'Filter by country name',
        'name': 'Search city name (case-insensitive substring)',
        'min_population': 'Minimum population threshold',
        'max_population': 'Maximum population threshold',
        'limit': 'Number of results to return (default=50)',
        'offset': 'Starting index for pagination (default=0)'
    })
    def get(self):
        """Return filtered list of cities."""
        country = request.args.get("country")
        name = request.args.get("name")
        min_pop = request.args.get("min_population", type=int)
        max_pop = request.args.get("max_population", type=int)
        limit = request.args.get("limit", default=50, type=int)
        offset = request.args.get("offset", default=0, type=int)

        cities = dc.get_all_cities()

        if country:
            cities = [c for c in cities if c.get("country") == country]
        if name:
            cities = [c for c in cities if name.lower() in c.get("name", "").lower()]
        if min_pop is not None:
            cities = [c for c in cities if c.get("population", 0) >= min_pop]
        if max_pop is not None:
            cities = [c for c in cities if c.get("population", 0) <= max_pop]

        # sorting support
        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order", "asc")

        if sort_by:
            reverse = sort_order.lower() == "desc"
            cities.sort(key=lambda c: c.get(sort_by, None), reverse=reverse)

        cities = cities[offset : offset + limit]
        return cities

    @api.expect(city_model)
    def post(self):
        """Add a new city with validation."""
        data = api.payload or {}

        # Strong validation
        msg, ok = validate_city_payload(data, partial=False)
        if not ok:
            return {"error": msg}, 400

        dc.add_city(data)
        return {'message': 'City added successfully', 'city': data}, 201

@api.route('/cities/<string:name>')
class CityByName(Resource):
    def get(self, name):
        # (unchanged)
        city = dc.get_city_by_name(name)
        if city:
            return city, 200
        return {'error': 'City not found'}, 404

    @api.expect(city_model)
    def put(self, name):
        """Update a city with validation."""
        updates = api.payload or {}

        # Strong validation (full update)
        msg, ok = validate_city_payload(updates, partial=False)
        if not ok:
            return {"error": msg}, 400

        if dc.update_city(name, updates):
            return {'message': 'City updated'}, 200
        return {'error': 'City not found'}, 404

    def delete(self, name):
        # (unchanged)
        if dc.delete_city(name):
            return {'message': 'City deleted'}, 200
        return {'error': 'City not found'}, 404
