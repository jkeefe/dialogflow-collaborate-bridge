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

# In[12]:


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
from gspread_pandas import Spread, Client

# variables we'll need
host = os.environ['DBHOST']
port = 3306
dbname = "collaborate"
user = os.environ['DBUSER']
password = os.environ['DBPASSWORD']


# In[13]:


#### Main function ####

def handler(incoming):
    
    ## Put code here
    
    # ## Get list of projects

    # In[15]:


    main_spread = Spread('1wZDpHfIqKBEhmS_F485kFKmrBUAbrfMqu2HW4NOY6BE')


    # In[16]:


    project_list = main_spread.sheet_to_df(index=0)


    # In[17]:


    project_list


    # In[18]:


    # create sqlalchemy engine
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                       .format(user=user,
                               pw=password,
                               host=host,
                               db=dbname))


    # In[19]:


    # open the database connection
    dbConnection    = engine.connect()


    # In[20]:


    # loop through all the projects
    for index, row in project_list.iterrows():
        
        project = row['dialogflow_project_id']
        spreadsheet_id = row['google_spreadsheet_id']
        
        # Get the project data we need
        df = pd.read_sql(f"SELECT `identifier`, `item_key`, `item_value` FROM `data_pieces` WHERE `project` = '{project}'", dbConnection)
        columns_df = pd.read_sql(f"SELECT * FROM `column_tracker` WHERE `project` = '{project}'", dbConnection)
        text_df = pd.read_sql(f"SELECT * FROM `text_log` WHERE `project` = '{project}'", dbConnection)
        first_contact_df = pd.read_sql(f"SELECT * FROM `first_contact` WHERE `project` = '{project}'", dbConnection)
        
        # pivot all the data pieces so columns along the top, identfiers as rows
        pivoted = df.pivot(index='identifier', columns='item_key', values=['item_value'])
        
        # flatten the column headers
        pivoted.columns = pivoted.columns.get_level_values(1)
        pivoted.reset_index(inplace=True) 
        
        # sort the columns by order they were created
        columns_df.sort_values(by=['created_at'], inplace=True)
        
        # recorder the columns of the pivoted table
        ordered_columns = columns_df['col'].tolist()
        ordered_columns.insert(0, "identifier")
        pivoted_ordered = pivoted[ordered_columns]
        
        # on the text_df (or log) table, do a "group by" by identifier
        # and also concatinate the items in the group
        text_concat = text_df.groupby(['identifier'])['raw_text'].apply(' | '.join).reset_index()

        # add the "raw_text" column to the table so far
        merge1 = pd.merge(pivoted_ordered, text_concat, on="identifier")
        
        # sort the list of first-contacts, and merge into the final table
        first_contact_df.sort_values(by=['created_at'], inplace=True)
        final_table = pd.merge(first_contact_df, merge1, on="identifier")
        
        # drop the project columns from the final_table for the spreadsheet
        final_table.drop(columns=['proj_ident_hash', 'project'], inplace = True)
        
        # establish the project spreadsheet and update the first sheet
        spread = Spread(spreadsheet_id)
        spread.df_to_sheet(final_table, index=False, sheet='Sheet1', start='A1', replace=True)
        
        print(f"Spreadsheet for {row['friendly_name']} updated.")
        


    # In[21]:


    # close the database
    dbConnection.close()


    # In[22]:


    print("All updates complete.")
    
    return "OK"

# In[14]:


########
