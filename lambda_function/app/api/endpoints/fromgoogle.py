from flask import jsonify

def handler(incoming):
    
    # incoming data will be structured as described
    # here: https:#cloud.google.com/dialogflow/docs/fulfillment-webhook#webhook_request
    from_google = incoming.body
    
    print("FROM_GOOGLE:", json.dumps(from_google) )
    
    # send back to google the messages already established there
    to_google = {
        "fulfillmentMessages": from_google.queryResult.fulfillmentMessages
    }
    
    print(from_google)
    
    return to_google