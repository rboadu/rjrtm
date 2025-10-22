from flask import Blueprint, jsonify, abort
import logging
from pymongo.errors import PyMongoError
from data.countries import read_all_countries, read_country_by_code

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