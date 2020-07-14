from flask import jsonify

def handler(req):
    
    response = jsonify([{'name': 'blue jay'}])
    
    return response