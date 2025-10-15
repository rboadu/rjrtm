from flask import Flask
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Server starting…")

app = Flask(__name__)

#remove later
# Root endpoint for health check
@app.route('/')
def root():
    logger.info("Successful request to '/'")
    return {'status': 'ok', 'service': 'rjrtm-api', 'version': '0.1'}


if __name__ == '__main__':
    app.run(debug=True)
