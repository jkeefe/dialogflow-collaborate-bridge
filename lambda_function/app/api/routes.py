from flask import Blueprint
from flask import request, jsonify
from .endpoints import bird

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


