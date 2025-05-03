import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
import random
import os

# Connecting to service account, sheets and drive
url = os.environ["SPREADSHEET_URL"]
account = os.environ["ACCOUNT_JSON"]
gc = gspread.service_account(filename=account)
sh = gc.open("Technovation Database").sheet1
creds = service_account.Credentials.from_service_account_file(account, scopes=['https://www.googleapis.com/auth/drive'])
database = build('drive', 'v3', credentials=creds)
data = sh.get_all_records()
df = pd.DataFrame(data)

# Randomly generating products
all_products = df["Product Name"].tolist()
random.shuffle(all_products)

for product in all_products:
    st.write(product)
# Show the dataframe
#st.write(df)

col1, col2, col3 = st.columns(3)


with col1:
    for i in range(200,350,50):
        tile = st.container(height = i)
        with tile:
            st.image("zelda_pfp.jpeg", width= i)
        
with col2:
    for i in range(300,150,-50):
        tile = st.container(height = i)
        with tile:
            st.image("riju_pfp2.jpeg", use_container_width="True")
            
with col3:
    for i in range(200,350,50):
        tile = st.container(height = i)
        with tile:
            st.image("zelda_pfp.jpeg", use_container_width="True")
