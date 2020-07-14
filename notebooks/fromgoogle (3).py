#!/usr/bin/env python
# coding: utf-8

# ## Packages

# From termainal I did:
# 
# ```
# pipenv install
# pipenv install jupyter pymysql sqlalchemy requests
# ```
# 

# In[19]:


import pymysql.cursors
import requests
from datetime import datetime
from sqlalchemy import create_engine
import hashlib 
import os
import json
import time
from collections import defaultdict
from flask import jsonify
import re

# variables we'll need
host = os.environ['DBHOST']
port = 3306
dbname = "collaborate"
user = os.environ['DBUSER']
password = os.environ['DBPASSWORD']


# In[20]:


def checkId(goog_data):
    
    # grab the last bit of the session ID to use as default
    # this regex does that somehow! :-)
    session = re.search(r'([^-]+$)', goog_data['session']).group(1)
    
    # no source, so return the session ID
    if 'source' not in goog_data['originalDetectIntentRequest'].keys():
        return f'test-session-{session}'

    
    # for twilio, it's the From phone number
    if goog_data['originalDetectIntentRequest']['source'] == "twilio":
        return goog_data['originalDetectIntentRequest']['payload']['data']['From']
    
    # otherwise we have an unknown platform
    return f'unknown platform {session}'


# In[11]:


def checkProject(goog_data):
    
    # determine which project were working with from the google request
    # based on the session URL
    # so projects/propublicafruittest-pyrata/agent/sessions/96c6d41c-b1b0-e1f8-4ca7-7e9945fa1a0a
    # => propublicafruittest-pyrata
    project = re.search(r'projects/(.*)/agent', goog_data['session']).group(1)
    
    return project


# In[22]:


def update_first_contact(connection, now, project, identifier):
        
    ## Add a new item to the first_contact, but chill 
    ## if it already exists
    
    # making a hash out of the entry
    # note that md5 is not secure (but works for our use)
    str2hash = f"{project}-{identifier}"      
    result = hashlib.md5(str2hash.encode()) 
    hexed = result.hexdigest()

    sql = "INSERT IGNORE INTO first_contact (`proj_ident_hash`, `created_at`, `project`, `identifier`) VALUES (%s, %s, %s, %s)"

    with connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, ( hexed, now, project, identifier ))

    connection.commit()
    
    return True


# In[13]:


def insert_into_pieces(connection, now, project, identifier, key, value):
    
    # making a hash out of the entry
    # note that md5 is not secure (but works for our use)
    str2hash = f"{project}-{identifier}-{key}"      
    result = hashlib.md5(str2hash.encode()) 
    hexed = result.hexdigest()
    
    # Create a new record
    sql = '''
    INSERT IGNORE INTO `data_pieces` 
        (`ident_key_hash`, `created_at`, `project`, `identifier`, `item_key`, `item_value`) 
    VALUES
        (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE `item_value` = %s
    '''
    
    with connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, ( hexed, now, project, identifier, key, value, value ))

    connection.commit()
    
    return True


# In[14]:


def add_to_text_log(connection, now, project, identifier, raw_text):
    
    # Create a new record
    sql = "INSERT INTO `text_log` (`created_at`, `project`, `identifier`, `raw_text`) VALUES (%s, %s, %s, %s)"

    with connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, ( now, project, identifier, raw_text ))

    connection.commit()

    return True
    


# In[15]:


def update_column_tracker(connection, now, project, column):
    
    # making a hash out of the entry
    # note that md5 is not secure (but works for our use)
    str2hash = f"{project}-{column}"      
    result = hashlib.md5(str2hash.encode()) 
    hexed = result.hexdigest()

    # Create a new record
    sql = "INSERT IGNORE INTO `column_tracker` (`col_project_hash`, `created_at`, `project`, `col`) VALUES (%s, %s, %s, %s)"

    with connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, ( hexed, now, project, column ))

    connection.commit()
    
    return True


# In[16]:


#### Main function ####

def handler(incoming):
    
    # incoming data will be structured as described
    # here: https:#cloud.google.com/dialogflow/docs/fulfillment-webhook#webhook_request
    
    #PROD from_google = incoming.json
    #DEV from_google = incoming
    from_google = incoming
    
    # Open the database connection
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 db=dbname,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    identifier = checkId(from_google)
    project = checkProject(from_google)
    user_said = from_google['queryResult']['queryText']
    now = datetime.now().isoformat(sep=' ', timespec='seconds') # => '2020-05-12 18:54:54'
    
    # Update the first_contact
    update_first_contact(connection, now, project, identifier)
    
    ## Add the intent as a column and a data_pieces item
    intent = from_google['queryResult']['intent']['displayName']
    update_column_tracker(connection, now, project, intent)
    insert_into_pieces(connection, now, project, identifier, intent, user_said) 
    
    ## Add every parameter as a column & data_pieces item
    parameters = from_google['queryResult']['parameters']
    
    for key in parameters.keys():
        if parameters[key] != "":
            
            ## sometimes google passes a json object here
            if isinstance(parameters[key], dict):
                info = json.dumps(parameters[key])
            else:
                info = parameters[key]
            
            update_column_tracker(connection, now, project, key)
            insert_into_pieces(connection, now, project, identifier, key, info)
    
    ## Add the raw text into the log
    add_to_text_log(connection, now, project, identifier, user_said) 
    
    # close the database
    connection.close()
    
    # send back to google the messages already established there
    to_google = {
        "fulfillmentMessages": from_google['queryResult']['fulfillmentMessages']
    }
    
    #PROD return jsonify(to_google)
    #DEV return (to_google)
    return (to_google)


# In[ ]:





# In[17]:


test_payload = {
    "responseId": "a96d4f9c-7b85-4a04-8b43-be609c8c695e-0f0e27e1",
    "queryResult": {
        "queryText": "Hola",
        "action": "input.welcome",
        "parameters": {},
        "allRequiredParamsPresent": True,
        "fulfillmentText": "Hello! What city are you in now?",
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "Hello! What city are you in now?"
                    ]
                }
            }
        ],
        "outputContexts": [
            {
                "name": "projects/propublicafruittest-pyrata/agent/sessions/96c6d41c-b1b0-e1f8-4ca7-7e9945fa1a0a/contexts/waiting-city",
                "lifespanCount": 5
            },
            {
                "name": "projects/propublicafruittest-pyrata/agent/sessions/96c6d41c-b1b0-e1f8-4ca7-7e9945fa1a0a/contexts/__system_counters__",
                "parameters": {
                    "no-input": 0,
                    "no-match": 0
                }
            }
        ],
        "intent": {
            "name": "projects/propublicafruittest-pyrata/agent/intents/10d4a02d-ac4c-4669-8782-8beffec91447",
            "displayName": "Default Welcome Intent"
        },
        "intentDetectionConfidence": 1,
        "languageCode": "en"
    },
    "originalDetectIntentRequest": {
        "payload": {}
    },
    "session": "projects/propublicafruittest-pyrata/agent/sessions/96c6d41c-b1b0-e1f8-4ca7-7e9945fa1a0a"
}


# In[23]:


## Trying it
handler(test_payload)


# In[ ]:





# In[ ]:




