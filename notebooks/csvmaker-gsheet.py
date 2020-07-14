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

# In[34]:


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


# In[35]:


#### Main function ####

def handler(incoming):
    
    ## Put code here
    
    
    return True


# In[36]:


########


# In[37]:


# create sqlalchemy engine
engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                   .format(user=user,
                           pw=password,
                           host=host,
                           db=dbname))


# In[38]:


# this will become a loop of projects pulled from a 
# master google spreadsheet
project = "propublicafruittest-pyrata"
spreadsheet_id = "1uHvY_Z0lpGdvAgkfTt-sNXMe5yGOiq0NZJju0aLej1E"


# In[39]:


# Get the data we need
dbConnection    = engine.connect()

df = pd.read_sql(f"SELECT `identifier`, `item_key`, `item_value` FROM `data_pieces` WHERE `project` = '{project}'", dbConnection)
columns_df = pd.read_sql(f"SELECT * FROM `column_tracker` WHERE `project` = '{project}'", dbConnection)
text_df = pd.read_sql(f"SELECT * FROM `text_log` WHERE `project` = '{project}'", dbConnection)
first_contact_df = pd.read_sql(f"SELECT * FROM `first_contact` WHERE `project` = '{project}'", dbConnection)

dbConnection.close()


# In[40]:


pivoted = df.pivot(index='identifier', columns='item_key', values=['item_value'])


# In[41]:


# pivoted


# In[42]:


pivoted.columns = pivoted.columns.get_level_values(1)
pivoted.reset_index(inplace=True) 


# In[43]:


# pivoted


# In[44]:


# pivoted.columns


# In[45]:


columns_df.sort_values(by=['created_at'], inplace=True)


# In[46]:


ordered_columns = columns_df['col'].tolist()


# In[47]:


ordered_columns.insert(0, "identifier")


# In[48]:


# ordered_columns


# In[49]:


pivoted_ordered = pivoted[ordered_columns]


# In[50]:


# pivoted_ordered


# In[51]:


# text_df


# In[52]:


text_concat = text_df.groupby(['identifier'])['raw_text'].apply(' | '.join).reset_index()


# In[53]:


merge1 = pd.merge(pivoted_ordered, text_concat, on="identifier")


# In[54]:


# merge1


# In[55]:


first_contact_df.sort_values(by=['created_at'], inplace=True)


# In[56]:


final_table = pd.merge(first_contact_df, merge1, on="identifier")


# In[57]:


final_table


# In[58]:


# drop the project columns for the spreadsheet
final_table.drop(columns=['proj_ident_hash', 'project'], inplace = True)


# In[59]:


# final_table


# In[ ]:





# ## Trying a service account

# In[ ]:





# In[60]:


spread = Spread(spreadsheet_id)


# In[61]:


spread.df_to_sheet(final_table, index=False, sheet='Sheet1', start='A1', replace=True)


# In[ ]:





# In[ ]:




