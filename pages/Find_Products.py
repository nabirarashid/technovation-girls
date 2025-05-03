import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
import random
import os
import sqlite3
from PIL import Image
import io

connect = sqlite3.connect("businesses.db")
cursor = connect.cursor()

# Connecting to service account, sheets and drive
url = os.environ["SPREADSHEET_URL"]
account = os.environ["ACCOUNT_JSON"]
gc = gspread.service_account(filename=account)
sh = gc.open("Technovation Database").sheet1
creds = service_account.Credentials.from_service_account_file(account, scopes=['https://www.googleapis.com/auth/drive'])
database = build('drive', 'v3', credentials=creds)
data = sh.get_all_records()
df = pd.DataFrame(data)
import sqlite3



# Randomly generating products
all_products = cursor.execute("""SELECT PRODUCT_NAME, PRODUCT_IMAGE FROM PRODUCTS;""")
products = cursor.fetchall()
random.shuffle(products)

for product in all_products:
    st.image(product)
# Show the dataframe
#st.write(df)

product_index = 0

num_rows = num_rows = len(products) // 3 + (1 if len(products) % 3 else 0)
for row in range(num_rows):
    cols = st.columns(3)
    for col in range(3):
        if product_index >= len(products):
            break
        product = products[product_index]
        image_binary = product[1]
        image = Image.open(io.BytesIO(image_binary))
        with cols[col]:
            st.image(image, use_container_width=True)
        product_index += 1
