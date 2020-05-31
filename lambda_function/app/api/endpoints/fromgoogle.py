from flask import jsonify
import json
import re

def checkId(goog_data):
    
    # grab the last bit of the session ID to use as default
    # this regex does that somehow! :-)
    session = re.match(r'/[^/]+$/', goog_data['session'])
    
    # no source, so return the session ID
    if 'source' not in goog_data['originalDetectIntentRequest'].keys():
        return `test-session-${session}`

    
    # for twilio, it's the From phone number
    if goog_data['originalDetectIntentRequest']['source'] == "twilio"):
        return goog_data['originalDetectIntentRequest']['payload']['data']['From']
    
    # otherwise we have an unknown platform
    return `unknown platform ${session}`


#### Main function

def handler(incoming):
    
    # incoming data will be structured as described
    # here: https:#cloud.google.com/dialogflow/docs/fulfillment-webhook#webhook_request
    from_google = incoming.json
    
    print("FROM_GOOGLE:", json.dumps(from_google) )
    
    # send back to google the messages already established there
    to_google = {
        "fulfillmentMessages": from_google['queryResult']['fulfillmentMessages']
    }
    
    return jsonify(to_google)