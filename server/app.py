from flask import Flask
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Server starting…")

app = Flask(__name__)

# Root endpoint for health check
@app.route('/')
def root():
    logger.info("Successful request to '/'")
    return {'status': 'ok', 'service': 'rjrtm-api', 'version': '0.1'}


if __name__ == '__main__':
    # Ensure DB connection is established when running the server directly
    try:
        import data.db_connect as dbc
        dbc.connect_db()
        logger.info('Connected to MongoDB')
    except Exception as e:
        logger.warning(f'Could not connect to MongoDB: {e}')
    app.run(debug=True)
