from urllib import request
from flask import Blueprint, jsonify, abort
import logging
from pymongo.errors import PyMongoError
from data.countries import read_all_countries, read_country_by_code, search_countries_by_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

countries_bp = Blueprint('countries', __name__, url_prefix='/countries')
logger.info("Countries blueprint initialized.")

@countries_bp.route('/', methods=['GET'])
def get_countries() -> jsonify:
    """Endpoint to get a list of available countries."""
    try:
        logger.info("Successful request to '/countries/'")
        countries = read_all_countries()
        for country in countries:
            country['_id'] = str(country['_id']) 
        return jsonify(countries)
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        abort(500, f"Database error: {e}")
    except Exception as e:
        logger.error(f"Error retrieving countries: {e}")
        abort(500, f"Error retrieving countries: {e}")

@countries_bp.route('/<string:code>', methods=['GET'])
def get_country_by_code(code: str) -> jsonify:
    """Endpoint to get a specific country by its code (e.g., 'UK')."""
    try:
        if not code.isalpha() or len(code) not in (2, 3) or not code.isupper():
            logger.warning(f"Invalid country code format: '{code}'")
            abort(400, f"Invalid country code format: {code}")
        logger.info(f"Request to '/countries/{code}'")
        country = read_country_by_code(code)
        if country:
            country['_id'] = str(country['_id'])
            return jsonify(country)
        else:
            logger.warning(f"Country with code '{code}' not found")
            abort(404, f"Country with code '{code}' not found")
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        abort(500, f"Database error: {e}")
    except Exception as e:
        logger.error(f"Error retrieving country: {e}")
        abort(500, f"Error retrieving country: {e}")

# Ideally a GET endpoint that makes use of the search_countries_by_name function in data/countries.py
# eg. @countries_bp.route('/search', methods=['GET'])
@countries_bp.route('/search', methods=['GET'])
def search_countries(country: str) -> jsonify:
    """Endpoint to search countries by name."""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            logger.warning("Search request with missing 'q' parameter")
            abort(400, "Search query parameter 'q' is required")
        
        logger.info(f"Search request for: '{query}'")
        countries = search_countries_by_name(query)
        
        for country in countries:
            country['_id'] = str(country['_id'])
        
        return jsonify(countries)
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        abort(500, f"Database error: {e}")
    except Exception as e: # basic exception catch-all for now
        logger.error(f"Error searching countries: {e}")
        abort(500, f"Error searching countries: {e}")

# Maype also implement a filter by region or continent if needed.
# e.g. @countries_bp.route('/region/<string:region>', methods=['GET'])