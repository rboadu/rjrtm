from flask import Blueprint, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

countries_bp = Blueprint('countries', __name__, url_prefix='/countries')
logger.info("Countries blueprint initialized.")

@countries_bp.route('/', methods=['GET'])
def get_countries() -> jsonify:
    """Endpoint to get a list of available countries."""
    logger.info("Successful request to '/countries/'")
    return jsonify([])