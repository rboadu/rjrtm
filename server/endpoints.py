from flask import request, abort
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
    delete_country_by_name
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
    'name': fields.String(required=True),
    'state': fields.String(required=True),
    'country': fields.String(required=True),
    'population': fields.Integer
})

country_model = api.model('Country', {
    'name': fields.String(required=True)
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
        data = api.payload
        try:
            inserted_id = ds.create_state(data)
            return {
                "message": "State created",
                "state": data
            }, 201
        except ValueError as e:
            return {"error": str(e)}, 400


@states_ns.route('/<string:country>/<string:code>')
class StateByCountryAndCode(Resource):

    def get(self, country, code):
        state = ds.read_state_by_code_and_country(code, country)
        if state:
            return state
        return {"error": "State not found"}, 404

    @api.expect(state_model)
    def put(self, country, code):
        data = api.payload
        updated = ds.update_state(code, country, data)
        if updated:
            return {"message": "State updated"}
        return {"error": "State not found"}, 404

    @api.expect(state_model)
    def patch(self, country, code):
        updates = api.payload or {}
        if not updates:                          # ← fix 1: return 400 for empty payload
            return {"error": "No fields provided"}, 400
        updated = ds.update_state(code, country, updates)
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
# CITY ENDPOINTS
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
        updates = api.payload

        pop_error = _validate_population(updates)  # ← fix 4: validate population on PUT
        if pop_error:
            return {"error": pop_error}, 400

        if dc.update_city(name, country, updates):
            return {"message": "City updated"}
        return {"error": "City not found"}, 404

    def delete(self, name, country):
        if dc.delete_city(name, country):
            return {"message": "City deleted"}
        return {"error": "City not found"}, 404


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
            country = api.payload
            new_id = create_country(country)
            return {
                "message": "Country created",
                "country": country
            }, 201
        except ValueError as e:
            return {"error": str(e)}, 409


@countries_ns.route('/<string:name>')
class CountryByName(Resource):

    def get(self, name):
        country = read_country_by_name(name)
        if country:
            return country
        return {"error": "Country not found"}, 404

    def delete(self, name):
        deleted = delete_country_by_name(name)
        if deleted:
            return {"message": "Country deleted"}
        return {"error": "Country not found"}, 404


@countries_ns.route('/search')
class CountrySearch(Resource):

    def get(self):
        q = request.args.get("q")
        if not q:
            abort(400, "Query parameter 'q' required")
        return search_countries_by_name(q)