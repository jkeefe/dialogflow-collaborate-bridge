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

# In[24]:


import pymysql.cursors
import requests
from datetime import datetime
from sqlalchemy import create_engine
import hashlib 
import os
import json
import time
from collections import defaultdict

# variables we'll need
host = os.environ['DBHOST']
port = 3306
dbname = "sam"
user = os.environ['DBUSER']
password = os.environ['DBPASSWORD']


# ## Game plan
# 
# - 

# In[25]:


list_endpoint_base = 'https://beta.sam.gov/api/prod/sgs/v1/search/?index=opp&q=&page=0&sort=-modifiedDate&mode=search&is_active=true&organization_id='
attachments_endpoint_base = 'https://beta.sam.gov/api/prod/opps/v3/opportunities/'

# ICE: organization_id=100012075
# FBI: organization_id=100500172
# DEA: organization_id=100500171
# State Dept: organization_id=100012062
# Secret Service: organization_id=100012967

organization_ids = ['100012075', '100500172', '100500171', '100012062', '100012062', '100012967']


# In[26]:


# Open the database connection
connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 db=dbname,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)


# In[27]:


slack_package = []

# loop through each search term
for search_term in organization_ids:
    
    # pause 5 seconds to be kind to the server
    time.sleep(6)
    
    endpoint = list_endpoint_base + search_term

    # hit sam.gov
    try:
        response = requests.get(endpoint)
    except requests.exceptions.RequestException as err:
        print (f"Had trouble getting the list for {search_term}:",err)
    
    data = response.json()
    results = data['_embedded']['results']
    record_qty = len(results)
    
    status = response.status_code
    print(f'Searched Sam.gov for {search_term}, got {record_qty} records, with status [{status}]')

    # loop through the search results
    for item in results:

        # making a hash out of the entry
        # note that md5 is not secure (but works for our use)
        str2hash = json.dumps(item)      
        result = hashlib.md5(str2hash.encode()) 
        hexed = result.hexdigest()
        now = datetime.now().isoformat(sep=' ', timespec='seconds') # => '2020-05-12 18:54:54'

        ## Add the hashed row to the database, but be chill 
        ## even if it already exists

        sql = f'''
            INSERT IGNORE INTO documents 
             (item_hash, created_at)
            VALUES
             ( '{hexed}', '{now}' )
        '''

        with connection.cursor() as cursor:
                # Create a new record
                cursor.execute(sql)

        connection.commit()

        ## If rows affected (cursor.rowcount) = 1, that means a row was inserted.
        ## And since we're using INSERT IGNORE, that means it didn't exist before
        ## ... so add it to the list of items to slack
        if cursor.rowcount == 1:
            
            # go get the attachements array for the item
            time.sleep(10) # be nice to the server
            attachments_endpoint = f"{attachments_endpoint_base}{item['_id']}/resources"
            
            try: 
                attachments_response = requests.get(attachments_endpoint)               
            except requests.exceptions.RequestException as err:
                print ("Had trouble getting some attachments:",err)
            
            attachments_data = attachments_response.json()
            status = attachments_response.status_code
            print(f'Hitting {attachments_endpoint}, got status [{status}]\n{attachments_data}')
            
            if '_embedded' in attachments_data.keys():
                attachments = attachments_data['_embedded']['opportunityAttachmentList'][0]['attachments']
            else:
                attachments = []
            
            # add the attachments list to the item
            item['attachments'] = attachments
            
            # print(json.dumps(item))
            
            # add the item to the slack package
            slack_package.append(item)

connection.close()


# In[ ]:





# Here's the [block kit tinker](https://api.slack.com/tools/block-kit-builder?mode=message&blocks=%5B%7B%22type%22%3A%22divider%22%7D%2C%7B%22type%22%3A%22section%22%2C%22text%22%3A%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%3Chttps%3A%2F%2Flink.com%7CLaw%20Enforcement%20Surveillance%20Equipment%3E%5Cn%22%7D%7D%2C%7B%22type%22%3A%22context%22%2C%22elements%22%3A%5B%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22US%20IMMIGRATION%20AND%20CUSTOMS%20ENFORCEMENT%22%7D%5D%7D%2C%7B%22type%22%3A%22section%22%2C%22text%22%3A%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%3Apage_facing_up%3A%20%3Chttps%3A%2F%2Ftest.com%2F%7Csome_document_0123.pdf%3E%22%7D%7D%5D) for this.

# ##  Send to Slack function

# In[28]:


def send_to_slack(payload):
    block_count = len(payload)
    print(f"Sending {block_count} block(s) to Slack ...")
    endpoint = os.environ['SLACK_URL']
    response = requests.post(endpoint, json=payload)
    print("Slack said: ", response)


# ## Building the slack message

# In[29]:


slack_payload = {
    "blocks": []
}

# loop through all the items in the package
for item in slack_package:
       
    slack_payload['blocks'].append({"type": "divider"})
    
    item_link = f"https://beta.sam.gov/opp/{item['_id']}/view"
    slack_payload['blocks'].append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"<{item_link}|{item['title']}>\n"
        }
    })
    
    if len(item['organizationHierarchy']) > 2:
        department = item['organizationHierarchy'][1]['name']
    else:
        department = item['organizationHierarchy'][0]['name']   
    
    slack_payload['blocks'].append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"{department}"
            }
        ]
    })
    
    # loop through the attachments, if any
    attachments_blob = ""
    for document in item['attachments']:
        
        if document['accessLevel'] != 'public':
            continue
            
        document_link = f"https://beta.sam.gov/api/prod/opps/v3/opportunities/resources/files/{document['resourceId']}/download"
        attachments_blob += f":page_facing_up: <{document_link}|{document['name']}>\n"
        
    if attachments_blob != "":
        
        slack_payload['blocks'].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{attachments_blob}"
            }
        })
    
        
    ## Slack limits each block set to 50
    if len(slack_payload['blocks']) > 45:
        
        # send what we have so far
        send_to_slack(slack_payload)
        
        # reset the payload
        slack_payload = {
            "blocks": []
        }

if len(slack_payload['blocks']) > 0:
    send_to_slack(slack_payload)
    
print("Done!")


# In[ ]:




