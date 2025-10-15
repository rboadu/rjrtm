from flask import Blueprint, jsonify, abort
import logging
from pymongo.errors import PyMongoError
from data.countries import read_all_countries

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