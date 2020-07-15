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

# In[29]:


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
import pandas as pd
import s3fs
import boto3

# variables we'll need
host = os.environ['DBHOST']
port = 3306
dbname = "collab"
user = os.environ['DBUSER']
password = os.environ['DBPASSWORD']


# In[30]:


#### Main function ####

def handler(incoming):
    
    ## Put code here
    # In[31]:


    #### TESTING ZONE #####


    # In[32]:


    # create sqlalchemy engine
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                       .format(user=user,
                               pw=password,
                               host=host,
                               db=dbname))


    # In[33]:


    # Get the data we need
    dbConnection    = engine.connect()

    df = pd.read_sql("SELECT `identifier`, `item_key`, `item_value` FROM `data_pieces`", dbConnection)
    columns_df = pd.read_sql("SELECT * FROM `column_tracker`", dbConnection)
    text_df = pd.read_sql("SELECT * FROM `text_log`", dbConnection)
    first_contact_df = pd.read_sql("SELECT * FROM `first_contact`", dbConnection)

    dbConnection.close()


    # In[34]:


    pivoted = df.pivot(index='identifier', columns='item_key', values=['item_value'])


    # In[35]:


    # pivoted


    # In[36]:


    pivoted.columns = pivoted.columns.get_level_values(1)
    pivoted.reset_index(inplace=True) 


    # In[37]:


    # pivoted


    # In[38]:


    # pivoted.columns


    # In[39]:


    columns_df.sort_values(by=['created_at'], inplace=True)


    # In[40]:


    ordered_columns = columns_df['col'].tolist()


    # In[41]:


    ordered_columns.insert(0, "identifier")


    # In[42]:


    # ordered_columns


    # In[43]:


    pivoted_ordered = pivoted[ordered_columns]


    # In[44]:


    # pivoted_ordered


    # In[45]:


    # text_df


    # In[46]:


    text_concat = text_df.groupby(['identifier'])['raw_text'].apply(' | '.join).reset_index()


    # In[47]:


    merge1 = pd.merge(pivoted_ordered, text_concat, on="identifier")


    # In[48]:


    # merge1


    # In[49]:


    first_contact_df.sort_values(by=['created_at'], inplace=True)


    # In[50]:


    final_table = pd.merge(first_contact_df, merge1, on="identifier")


    # In[51]:


    # final_table


    # In[52]:


    final_table.to_csv(f"{dbname}-export.csv", index=False)


    # In[ ]:





    # In[53]:


    final_table.to_csv(f's3://collab-bridge/{dbname}-export.csv', index=False)


    # In[55]:


    ## Make it public
    s3 = boto3.resource('s3')
    s3.Object('collab-bridge', f'{dbname}-export.csv').Acl().put(ACL='public-read')


    # In[56]:


    ## Note: Testing URL is https://collab-bridge.s3.amazonaws.com/collab-export.csv

    
    return True






