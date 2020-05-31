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

# In[81]:


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
dbname = "collab"
user = os.environ['DBUSER']
password = os.environ['DBPASSWORD']


# In[90]:


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


# In[97]:


def update_first_contact(connection, now, identifier):
        
    ## Add a new item to the first_contact, but chill 
    ## if it already exists

    sql = "INSERT IGNORE INTO first_contact (`created_at`, `identifier`) VALUES (%s, %s)"

    with connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, ( now, identifier ))

    connection.commit()
    
    return True


# In[98]:


def insert_into_log(connection, now, identifier, key, value):
    
    # Create a new record
    sql = "INSERT INTO `log` (`created_at`, `identifier`, `item_key`, `item_value`) VALUES (%s, %s, %s, %s)"

    with connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, ( now, identifier, key, value ))

    connection.commit()
    
    return True


# In[99]:


def update_column_tracker(connection, now, column):

    # Create a new record
    sql = "INSERT IGNORE INTO `column_tracker` (`created_at`, `col`) VALUES (%s, %s)"

    with connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, ( now, column ))

    connection.commit()
    
    return True


# In[100]:


#### Main function ####

def handler(incoming):
    
    # incoming data will be structured as described
    # here: https:#cloud.google.com/dialogflow/docs/fulfillment-webhook#webhook_request
    
    from_google = incoming.json
    
    # Open the database connection
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 db=dbname,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    identifier = checkId(from_google)
    user_said = from_google['queryResult']['queryText']
    now = datetime.now().isoformat(sep=' ', timespec='seconds') # => '2020-05-12 18:54:54'
    
    # Update the first_contact
    update_first_contact(connection, now, identifier)
    
    ## Add the intent as a column and a log item
    intent = from_google['queryResult']['intent']['displayName']
    update_column_tracker(connection, now, intent)
    insert_into_log(connection, now, identifier, intent, user_said) 
    
    ## Add every parameter as a column & log item
    parameters = from_google['queryResult']['parameters']
    
    for key in parameters.keys():
        if parameters[key] != "":
            
            ## sometimes google passes a json object here
            if isinstance(parameters[key], dict):
                info = json.dumps(parameters[key])
            else:
                info = parameters[key]
            
            update_column_tracker(connection, now, key)
            insert_into_log(connection, now, identifier, key, info)
    
    ## Add the raw text into the log
    insert_into_log(connection, now, identifier, "raw_text", user_said) 
    
    # close the database
    connection.close()
    
    # send back to google the messages already established there
    to_google = {
        "fulfillmentMessages": from_google['queryResult']['fulfillmentMessages']
    }
    
    return jsonify(to_google)
    



