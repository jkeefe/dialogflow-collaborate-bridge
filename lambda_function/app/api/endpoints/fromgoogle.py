from flask import jsonify
import json

def handler(incoming):
    
    # incoming data will be structured as described
    # here: https:#cloud.google.com/dialogflow/docs/fulfillment-webhook#webhook_request
    from_google = incoming.json
    
    print("FROM_GOOGLE:", json.dumps(from_google) )
    
    # send back to google the messages already established there
    to_google = {
        "fulfillmentMessages": from_google.queryResult.fulfillmentMessages
    }
    
    return jsonify(to_google)