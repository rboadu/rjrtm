from flask import Flask, jsonify, request, abort
from flask_restx import Resource, Api, fields
from flask_cors import CORS
import data.states as ds
import data.cities as dc
from werkzeug.exceptions import HTTPException
import logging
from pymongo.errors import PyMongoError
from data.countries import read_all_countries, read_country_by_code, search_countries_by_name, create_country, delete_country_by_code


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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==========================
# Models
# ==========================

# add country
state_model = api.model('State', {
    'code': fields.String(required=True, description='State code, e.g. NY'),
    'name': fields.String(required=True, description='State name, e.g. New York'),
    'country': fields.String(required=False, description='Country of the state', example='USA')

})

# add the state
city_model = api.model('City', {
    'name': fields.String(required=True, description='City name'),
    'country': fields.String(required=True, description='Country where the city is located'),
    'population': fields.Integer(description='Population of the city')
})


country_model = api.model('Country', {
    'code': fields.String(required=True, description='ISO country code (2 or 3 letters)'),
    'name': fields.String(required=True, description='Country name')
})

error_model = api.model('ErrorResponse', {
    'error': fields.String(description='Error message')
})

city_created_model = api.model('CityCreatedResponse', {
    'message': fields.String(example='City added successfully'),
    'city': fields.Nested(city_model)
})

journal_model = api.model('JournalEntry', {
    'entry': fields.String(required=True, description='Journal entry text')
})

# ==========================
# General Endpoints
# ==========================

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


# ==========================
# State Endpoints 
# ==========================
states_ns = api.namespace('states', description='States operations')

@states_ns.route('')
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
        inserted_id = ds.create_state(data)
        # avoid returning raw ObjectId which is not JSON serializable
        state_copy = dict(data or {})
        # prefer any _id already present on the dict (pymongo may have mutated it)
        returned_id = state_copy.get('_id', inserted_id)
        try:
            state_copy['_id'] = str(returned_id)
        except Exception:
            state_copy['_id'] = returned_id

        return {'message': 'State added successfully', 'state': state_copy}, 201


@states_ns.route('/bulk')
class StatesBulk(Resource):
    @api.expect([state_model])
    def post(self):
        """Create multiple states in a single request.

        Expects a JSON array of state documents.
        """
        payload = api.payload
        if payload is None:
            return {'error': 'Payload required (list of state documents)'}, 400

        if not isinstance(payload, list):
            return {'error': 'Payload must be a list of state documents'}, 400

        # validate basic shape
        valid_docs = []
        errors = []
        for idx, item in enumerate(payload):
            if not isinstance(item, dict):
                errors.append(f'Item {idx} is not an object')
                continue
            if 'code' not in item or 'name' not in item:
                errors.append(f'Item {idx} missing required fields: code and name')
                continue
            valid_docs.append(item)

        if not valid_docs:
            return {'error': 'No valid state documents to insert', 'details': errors}, 400

        try:
            inserted_ids = ds.create_states_bulk(valid_docs)
        except Exception as e:
            logger.exception('Bulk insert failed')
            return {'error': 'Bulk insert failed', 'details': str(e)}, 500

        return {'created': inserted_ids, 'errors': errors}, 201


@states_ns.route('/<string:code>')
class StateByCode(Resource):
    def get(self, code):
        """Return a specific state by code."""
        state = ds.read_state_by_code(code)
        if state:
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


@states_ns.route('/<string:code>/patch')
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


@states_ns.route('/country/<string:country>')
class StatesByCountry(Resource):
    @api.marshal_list_with(state_model)
    def get(self, country):
        """Return all states for a given country."""
        states = ds.read_states_by_country(country)
        if states:
            return states, 200
        return {'error': f'No states found for country: {country}'}, 404


# ==========================
# City Validation Helper
# ==========================

def validate_city_payload(data, partial=False):
    allowed_fields = {"name", "country", "population"}
    required_fields = {"name", "country"}

    # Reject unknown fields
    for field in data:
        if field not in allowed_fields:
            return f"Unknown field: '{field}'", False

    # Require mandatory fields unless partial=True
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


# ==========================
# City Endpoints 
# ==========================

cities_ns = api.namespace('cities', description='Cities operations')

@cities_ns.route('')
class Cities(Resource):

    @api.marshal_list_with(city_model)
    @api.doc(
        description="Retrieve a list of cities with optional filtering, sorting, and pagination.",
        params={
            'country': 'Filter by country name',
            'name': 'Case-insensitive substring search on city name',
            'min_population': 'Minimum population value',
            'max_population': 'Maximum population value',
            'limit': 'Number of results to return (default=50)',
            'offset': 'Offset for pagination (default=0)',
            'sort_by': 'Sort by field: name | country | population',
            'sort_order': 'Sort order: asc | desc'
        },
        responses={
            200: "List of cities",
            400: ("Invalid query parameter", error_model)
        }
    )
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

        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order", "asc")

        if sort_by:
            reverse = sort_order.lower() == "desc"
            cities.sort(key=lambda c: c.get(sort_by, None), reverse=reverse)

        cities = cities[offset : offset + limit]
        return cities

    @api.expect(city_model)
    @api.response(201, 'City created successfully', city_created_model)
    @api.response(400, 'Invalid city payload', error_model)
    @api.response(409, 'City already exists', error_model)
    def post(self):
        """Add a new city with validation."""
        data = api.payload or {}

        msg, ok = validate_city_payload(data, partial=False)
        if not ok:
            return {"error": msg}, 400

        try:
            created_city = dc.add_city(data)   # ← USE RETURN VALUE
            return {
                'message': 'City added successfully',
                'city': created_city
            }, 201
        except ValueError as e:
            return {"error": str(e)}, 409


@cities_ns.route('/<string:name>/<string:country>')
class CityByNameAndCountry(Resource):

    @api.response(200, 'City retrieved successfully', city_model)
    @api.response(404, 'City not found', error_model)
    def get(self, name, country):
        """Get a specific city by name and country."""
        city = dc.get_city_by_name_and_country(name, country)
        if city:
            return city, 200
        return {'error': 'City not found'}, 404

    @api.expect(city_model)
    @api.response(200, 'City updated successfully')
    @api.response(400, 'Invalid update payload', error_model)
    @api.response(404, 'City not found', error_model)
    def put(self, name, country):
        """Update a city with validation."""
        updates = api.payload or {}

        msg, ok = validate_city_payload(updates, partial=False)
        if not ok:
            return {"error": msg}, 400

        if dc.update_city(name, country, updates):
            return {'message': 'City updated'}, 200
        return {'error': 'City not found'}, 404

    @api.response(200, 'City deleted successfully')
    @api.response(404, 'City not found', error_model)
    def delete(self, name, country):
        """Delete a specific city by name and country."""
        if dc.delete_city(name, country):
            return {'message': 'City deleted'}, 200
        return {'error': 'City not found'}, 404


@cities_ns.route('/<string:name>')
class CityByName(Resource):

    @api.response(200, 'City retrieved successfully', city_model)
    @api.response(404, 'City not found', error_model)
    def get(self, name):
        """Get a specific city by name (first match)."""
        city = dc.get_city_by_name(name)
        if city:
            return city, 200
        return {'error': 'City not found'}, 404

    @api.expect(city_model)
    @api.response(200, 'City updated successfully')
    @api.response(400, 'Invalid update payload', error_model)
    @api.response(404, 'City not found', error_model)
    def put(self, name):
        """Update a city by name (uses first matching city to determine country)."""
        updates = api.payload or {}

        msg, ok = validate_city_payload(updates, partial=True)
        if not ok:
            return {"error": msg}, 400

        city = dc.get_city_by_name(name)
        if not city:
            return {'error': 'City not found'}, 404

        country = city.get('country')
        if dc.update_city(name, country, updates):
            return {'message': 'City updated'}, 200

        return {'error': 'City not found'}, 404

    @api.response(200, 'City deleted successfully')
    @api.response(404, 'City not found', error_model)
    def delete(self, name):
        """Delete a specific city by name (uses first match to determine country)."""
        city = dc.get_city_by_name(name)
        if not city:
            return {'error': 'City not found'}, 404
        country = city.get('country')
        if dc.delete_city(name, country):
            return {'message': 'City deleted'}, 200
        return {'error': 'City not found'}, 404
    

# ==========================
# Country Endpoints 
# ==========================

countries_ns = api.namespace('countries', description='Country operations')

logger.info("Countries blueprint initialized.")

@countries_ns.route('/')
class CountriesList(Resource):
    """Retrieve all countries or create a new country"""
    
    @api.marshal_list_with(country_model, mask=None)
    @api.doc(description="Retrieve all countries from the database")
    @api.response(200, 'List of countries')
    @api.response(500, 'Database error', error_model)
    def get(self):
        """Get all countries."""
        try:
            logger.info("Successful request to '/countries/'")
            countries = read_all_countries()
            return countries
        except PyMongoError as e:
            logger.error(f"Database error: {e}")
            abort(500, f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error retrieving countries: {e}")
            abort(500, str(e))

    @api.expect(country_model)
    @api.response(201, 'Country added successfully')
    @api.response(400, 'Invalid payload', error_model)
    @api.response(409, 'Country already exists', error_model)
    @api.response(500, 'Database error', error_model)
    def post(self):
        """Create a new country."""
        try:
            logger.info("Request to create a new country")
            country = api.payload or {}

            # Validate fields
            if "code" not in country or "name" not in country:
                return {"error": "Both 'code' and 'name' are required"}, 400

            code = country.get("code")
            if not code.isalpha() or len(code) not in (2, 3) or not code.isupper():
                return {"error": "Invalid country code format"}, 400

            # Try to create
            new_id = create_country(country)

            return {
                "message": "Country created successfully",
                "country": {**country, "_id": str(new_id)}
            }, 201

        except PyMongoError as e:
            logger.error(f"Database error: {e}")
            abort(500, f"Database error: {e}")

        except Exception as e:
            logger.error(f"Unexpected error creating country: {e}")
            abort(500, str(e))


@countries_ns.route('/<string:code>')
class CountryByCode(Resource):
    """Get a specific country by code"""
    
    @api.marshal_with(country_model, mask=None)
    @api.doc(description="Retrieve a specific country by its code")
    @api.response(200, 'Country retrieved successfully')
    @api.response(400, 'Invalid country code format', error_model)
    @api.response(404, 'Country not found', error_model)
    @api.response(500, 'Database error', error_model)
    def get(self, code: str):
        """Get a country by code."""
        try:
            if not code.isalpha() or len(code) not in (2, 3) or not code.isupper():
                logger.warning(f"Invalid country code format: '{code}'")
                abort(400, f"Invalid country code format: {code}")

            logger.info(f"Request to '/countries/{code}'")
            country = read_country_by_code(code)

            if country:
                return country
            else:
                logger.warning(f"Country with code '{code}' not found")
                abort(404, f"Country with code '{code}' not found")

        except HTTPException:
            raise
        except PyMongoError as e:
            logger.error(f"Database error: {e}")
            abort(500, f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error retrieving country: {e}")
            abort(500, str(e))


@countries_ns.route('/search')
class CountrySearch(Resource):
    """Search endpoint for countries"""
    
    @api.marshal_list_with(country_model, mask=None)
    @api.doc(
        description="Search for countries by name (case-insensitive partial match)",
        params={'q': {'description': 'Search query string', 'type': 'string', 'required': True}}
    )
    @api.response(200, 'Search results')
    @api.response(400, 'Missing search query', error_model)
    @api.response(500, 'Database error', error_model)
    def get(self):
        """Search countries by name."""
        try:
            query = request.args.get('q', '').strip()
            if not query:
                abort(400, "Search query parameter 'q' is required")

            logger.info(f"Search request for: '{query}'")
            countries = search_countries_by_name(query)

            return countries

        except HTTPException:
            raise
        except PyMongoError as e:
            logger.error(f"Database error: {e}")
            abort(500, f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error searching countries: {e}")
            abort(500, str(e))


@countries_ns.route('/delete/<string:code>')
class CountryDelete(Resource):
    """Delete a specific country"""
    
    @api.doc(description="Delete a country by its code")
    @api.response(200, 'Country deleted successfully')
    @api.response(400, 'Invalid country code format', error_model)
    @api.response(404, 'Country not found', error_model)
    @api.response(500, 'Database error', error_model)
    def delete(self, code: str):
        """Delete a country by code."""
        try:
            if not code.isalpha() or len(code) not in (2, 3) or not code.isupper():
                logger.warning(f"Invalid country code format: '{code}'")
                abort(400, f"Invalid country code format: {code}")

            logger.info(f"Request to delete country: '{code}'")
            
            deleted_count = delete_country_by_code(code)

            if deleted_count > 0:
                return {'message': f"Country '{code}' deleted successfully"}, 200
            else:
                logger.warning(f"Country with code '{code}' not found")
                abort(404, f"Country with code '{code}' not found")

        except HTTPException:
            raise
        except PyMongoError as e:
            logger.error(f"Database error: {e}")
            abort(500, f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error deleting country: {e}")
            abort(500, str(e))