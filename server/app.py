from flask import Flask
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Server starting…")

# -------------------------------------------------
# SINGLE Flask app instance
# -------------------------------------------------

app = Flask(__name__)


# -------------------------------------------------
# Register API routes (VERY IMPORTANT)
# -------------------------------------------------

import server.endpoints


# -------------------------------------------------
# Run server
# -------------------------------------------------

if __name__ == '__main__':
    try:
        import data.db_connect as dbc
        dbc.connect_db()
        logger.info('Connected to MongoDB')
    except Exception as e:
        logger.warning(f'Could not connect to MongoDB: {e}')

    app.run(debug=True)