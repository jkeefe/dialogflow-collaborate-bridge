from flask import Blueprint
from flask import request, jsonify

from .endpoints import bird
from .endpoints import fromgoogle
from .endpoints import updatesheets

api = Blueprint('api', __name__)

@api.route('/', methods=('GET', 'POST'))
def handle_root():
    if request.method == 'POST':
        return 'ok'

    return jsonify([{'data': 'Hello from your flask app!'}])


@api.route('/artists', methods=('GET', 'POST'))
def handle_artists():
    if request.method == 'POST':
        return 'ok'

    return jsonify([{'name': 'enya'}])
    
    
## also can import other endpoints

@api.route('/bird', methods=('GET', 'POST'))
def handle_bird():

    # pass the request to the bird handler
    return bird.handler(request)

@api.route('/fromgoogle', methods=('GET', 'POST'))
def handle_fromgoogle():

    # pass the request to the handler
    return fromgoogle.handler(request)

@api.route('/updatesheets', methods=('GET', 'POST'))
def handle_updatesheets():

    # pass the request to the handler
    return updatesheets.handler(request)
    
    