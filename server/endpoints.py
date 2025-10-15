"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask  # , request
from flask_restx import Resource, Api  # , fields  # Namespace
from flask_cors import CORS
from flask_restx import fields
import data.states as ds

# import werkzeug.exceptions as wz

app = Flask(__name__)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
MESSAGE = 'Message'
JOURNAL_EP = '/journal'
JOURNAL_RESP = 'journal'

state_model = api.model('State', {
    'code': fields.String(required=True, description='State code, e.g. NY'),
    'name': fields.String(required=True, description='State name, e.g. New York')
})


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a sorted list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(JOURNAL_EP)
class Journal(Resource):
    """
    This class will serve as a simple journal endpoint.
    """
    def get(self):
        """
        The `get()` method will return a simple message.
        """
        return {JOURNAL_RESP: 'RJRTM Journal'}
    
journal_model = api.model('JournalEntry', {
    'entry': fields.String(required=True, description='Journal entry text')
})

@api.route('/journal/add')
class JournalAdd(Resource):
    @api.expect(journal_model)
    def post(self):
        data = api.payload
        entry = data.get('entry')
        if not entry:
            return {'error': 'Entry is required'}, 400
        return {'message': 'Entry added', 'entry': entry}, 201


@api.route('/states')
class States(Resource):
    @api.marshal_list_with(state_model)
    def get(self):
        """Return all states from the database."""
        states = ds.read_all_states()
        return states

    @api.expect(state_model)
    def post(self):
        """Add a new state."""
        data = api.payload
        ds.create_state(data)
        return {'message': 'State added successfully', 'state': data}, 201