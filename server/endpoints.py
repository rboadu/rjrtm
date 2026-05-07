from flask import Flask, request, abort
from flask_restx import Resource, Api, fields
from flask_cors import CORS
from server.app import app
import data.states as ds
import data.cities as dc
import logging
from pymongo.errors import PyMongoError
from werkzeug.exceptions import HTTPException

from data.countries import (
    read_all_countries,
    read_country_by_name,
    search_countries_by_name,
    create_country,
    delete_country_by_name,
    update_country_by_name,
)

CORS(app)
api = Api(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================
# Models
# ==========================

state_model = api.model('State', {
    'code': fields.String(required=True),
    'name': fields.String(required=True),
    'country': fields.String(required=True)
})

city_model = api.model('City', {
    'name': fields.String(required=True, description='City name'),
    'state': fields.String(required=True, description='State or region for the city'),
    'country': fields.String(required=True, description='Country where the city is located'),
    'population': fields.Integer(description='Population of the city')
})

country_model = api.model('Country', {
    'name': fields.String(required=True),
    'password': fields.String(required=False),
})

country_update_model = api.model('CountryUpdate', {
    'name': fields.String(required=False),
    'password': fields.String(required=False),
})

error_model = api.model('ErrorResponse', {
    'error': fields.String
})

# ==========================
# STATE ENDPOINTS
# ==========================

states_ns = api.namespace('states', description='States operations')

@states_ns.route('')
class States(Resource):

    @api.marshal_list_with(state_model)
    def get(self):
        return ds.read_all_states()

    @api.expect(state_model)
    def post(self):
        """Add a new state."""
        data = api.payload or {}
        if "code" not in data or "name" not in data:
            return {"error": "Both 'code' and 'name' are required"}, 400

        existing = ds.read_state_by_code(data.get("code"))
        if existing:
            return {"error": "State already exists"}, 409
        try:
            inserted_id = ds.create_state(data)
        except ValueError as e:
            return {"error": str(e)}, 409
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
        seen_codes = set()
        for idx, item in enumerate(payload):
            if not isinstance(item, dict):
                errors.append(f'Item {idx} is not an object')
                continue
            if 'code' not in item or 'name' not in item:
                errors.append(f'Item {idx} missing required fields: code and name')
                continue
            code = item.get("code")
            if code in seen_codes:
                errors.append(f"Item {idx} duplicate code in payload: {code}")
                continue
            if ds.read_state_by_code(code):
                errors.append(f"Item {idx} duplicate code in database: {code}")
                continue
            seen_codes.add(code)
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
            return state
        return {"error": "State not found"}, 404

    @api.expect(state_model)
    def put(self, code):
        """Update a state by code."""
        data = api.payload or {}
        if "code" in data and data["code"] != code:
            return {"error": "State code cannot be changed"}, 400
        updated = ds.update_state(code, data)
        if updated:
            return {"message": "State updated"}
        return {"error": "State not found"}, 404

    @api.expect(state_model)
    def patch(self, code):
        """Partially update a state by code."""
        data = api.payload or {}
        if not data:
            return {'error': 'No update fields provided'}, 400
        if "code" in data and data["code"] != code:
            return {"error": "State code cannot be changed"}, 400
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
        if "code" in updates and updates["code"] != code:
            return {"error": "State code cannot be changed"}, 400
        updated = ds.update_state(code, updates)
        if updated:
            return {"message": "State updated"}
        return {"error": "State not found"}, 404

    def delete(self, country, code):
        deleted = ds.delete_state(code, country)
        if deleted:
            return {"message": "State deleted"}
        return {"error": "State not found"}, 404


@states_ns.route('/country/<string:country>')
class StatesByCountry(Resource):

    @api.marshal_list_with(state_model)
    def get(self, country):
        states = ds.read_states_by_country(country)
        if states:
            return states
        return {"error": "No states found"}, 404


# ==========================
# City Validation Helper
# ==========================

def validate_city_payload(data, partial=False):
    allowed_fields = {"name", "state", "country", "population"}
    required_fields = {"name", "state", "country"}

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

    if "state" in data and not isinstance(data["state"], str):
        return "'state' must be a string", False

    if "population" in data:
        pop = data["population"]
        if not isinstance(pop, int) or pop < 0:
            return "'population' must be a non-negative integer", False

    return "", True


# ==========================
# City Endpoints 
# ==========================

cities_ns = api.namespace('cities', description='Cities operations')


def _validate_population(data):
    """Returns an error string if population is invalid, else None."""
    population = data.get("population")
    if population is not None and population < 0:
        return "Population must be a non-negative integer"
    return None


@cities_ns.route('')
class Cities(Resource):

    def get(self):                               # ← fix 5: support query filters
        all_cities = dc.get_all_cities()
        name_filter = request.args.get("name")
        min_pop = request.args.get("min_population", type=int)
        max_pop = request.args.get("max_population", type=int)

        if name_filter:
            all_cities = [c for c in all_cities if name_filter.lower() in c.get("name", "").lower()]
        if min_pop is not None:
            all_cities = [c for c in all_cities if c.get("population", 0) >= min_pop]
        if max_pop is not None:
            all_cities = [c for c in all_cities if c.get("population", 0) <= max_pop]

        return all_cities

    @api.expect(city_model)
    def post(self):
        data = api.payload

        pop_error = _validate_population(data)   # ← fix 4: validate population
        if pop_error:
            return {"error": pop_error}, 400

        try:
            created = dc.add_city(data)
            return {
                "message": "City created",
                "city": created
            }, 201
        except ValueError as e:
            msg = str(e)
            if "already exists" in msg:          # ← fix 2: 409 only for duplicates
                return {"error": msg}, 409
            return {"error": msg}, 400           # ← missing fields, bad country/state


@cities_ns.route('/<string:name>/<string:country>')
class CityByNameAndCountry(Resource):

    def get(self, name, country):
        city = dc.get_city_by_name_and_country(name, country)
        if city:
            return city
        return {"error": "City not found"}, 404

    @api.expect(city_model)
    def put(self, name, country):
        """Update a city with validation."""
        updates = api.payload or {}

        msg, ok = validate_city_payload(updates, partial=False)
        if not ok:
            return {"error": msg}, 400

        next_name = updates.get("name", name)
        next_country = updates.get("country", country)
        if (next_name, next_country) != (name, country):
            existing = dc.get_city_by_name_and_country(next_name, next_country)
            if existing:
                return {"error": "City already exists"}, 409

        if dc.update_city(name, country, updates):
            return {"message": "City updated"}
        return {"error": "City not found"}, 404

    def delete(self, name, country):
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
        next_name = updates.get("name", name)
        next_country = updates.get("country", country)
        if (next_name, next_country) != (name, country):
            existing = dc.get_city_by_name_and_country(next_name, next_country)
            if existing:
                return {"error": "City already exists"}, 409
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
    
@cities_ns.route('/bulk')
class CitiesBulk(Resource):

    @api.expect([city_model])
    @api.response(201, 'Cities created successfully')
    @api.response(400, 'Invalid payload', error_model)
    @api.response(409, 'No cities created', error_model)
    def post(self):
        """Create multiple cities in one request."""
        payload = api.payload

        if not isinstance(payload, list):
            return {'error': 'Payload must be a list of city objects'}, 400

        created = []
        errors = []

        for idx, city in enumerate(payload):
            msg, ok = validate_city_payload(city, partial=False)
            if not ok:
                errors.append(f'Item {idx}: {msg}')
                continue

            try:
                created_city = dc.add_city(city)
                created.append(created_city)
            except ValueError as e:
                errors.append(f'Item {idx}: {str(e)}')

        if not created:
            return {
                'error': 'No cities created',
                'details': errors
            }, 409

        return {
            'message': 'Bulk city creation complete',
            'created': created,
            'errors': errors
        }, 201

    

# ==========================
# COUNTRY ENDPOINTS
# ==========================

countries_ns = api.namespace('countries', description='Country operations')

@countries_ns.route('/')
class Countries(Resource):

    def get(self):
        return read_all_countries()

    @api.expect(country_model)
    def post(self):
        try:
            country = dict(api.payload or {})
            create_country(country)
            response_country = dict(country)
            response_country.pop('password', None)
            return {
                "message": "Country created",
                "country": response_country
            }, 201

        except ValueError as e:
            return {"error": str(e)}, 409

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