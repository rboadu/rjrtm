from flask import Flask
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Server starting…")


import os
from flask import jsonify, send_file, abort

app = Flask(__name__)


# Root endpoint for health check
@app.route('/')
def root():
    logger.info("Successful request to '/'")
    return {'status': 'ok', 'service': 'rjrtm-api', 'version': '0.1'}

# Endpoint to list all log files in /var/log
@app.route('/dev/logs', methods=['GET'])
def list_logs():
    log_dir = '/var/log'
    try:
        files = [f for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))]
        return jsonify({'log_files': files})
    except Exception as e:
        logger.warning(f'Error listing log files: {e}')
        abort(500, description='Could not list log files')


if __name__ == '__main__':
    # Ensure DB connection is established when running the server directly
    try:
        import data.db_connect as dbc
        dbc.connect_db()
        logger.info('Connected to MongoDB')
    except Exception as e:
        logger.warning(f'Could not connect to MongoDB: {e}')
    app.run(debug=True)