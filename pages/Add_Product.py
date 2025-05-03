import streamlit as st
import gspread
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import requests
import os
from create_database import make_database
import sqlite3
connect = sqlite3.connect("businesses.db")
cursor = connect.cursor()




st.set_page_config(
    page_title="Add a Product",
    page_icon="",
)

# Connecting to service account, sheets and drive
account = os.environ["ACCOUNT_JSON"]
gc = gspread.service_account(filename=account)
sh = gc.open("Technovation Database").sheet1

creds = service_account.Credentials.from_service_account_file(account, scopes=['https://www.googleapis.com/auth/drive'])
database = build('drive', 'v3', credentials=creds)

# Make database
make_database()


# Checking if form has already been submitted
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

if st.session_state.submitted:
    st.session_state.business_name = ""
    st.session_state.product_name = ""
    st.session_state.product_price = 0.0
    st.session_state.reset_form = False

def addProduct():
    # Resetting form
    if st.session_state.submitted:
        # Reset form fields before rendering
        st.session_state.business_name = ""
        st.session_state.product_name = ""
        st.session_state.product_price = 0.0
        st.session_state.submitted = False
    
    # Making actual form
    product_form = st.form("product_submission")
    with product_form:
        st.write("Add a product!")

        # Basic business and product information
        business_name = product_form.text_input("Business name: ", key="business_name")
        product_name = product_form.text_input("Product name: ", key="product_name")
        product_price = product_form.number_input("Product price: ", key="product_price")
        product_description = product_form.text_input("Product description: ", key="product_description")
        product_tags = product_form.text_input("Please enter some tags to help people find your product, separated by commas: ", key="product_tags")

        # Upload an image
        product_picture = product_form.file_uploader("Upload a picture of your product", type=['jpg', 'png'], accept_multiple_files=False)
        if product_picture:
            image = product_picture.read()     

        submit = st.form_submit_button('Add')

        # Updating spreadsheet
        if submit:
            if product_name == "":
                st.error("Please enter the name of your product!")
            elif not product_picture:
                st.error("Please upload an image of your product!")
            else:
                # Inserting business name into database if it doesn't exist
                cursor.execute("INSERT INTO BUSINESSES (NAME) VALUES (?);", (business_name,))
                cursor.execute("SELECT last_insert_rowid();")
                row_id = cursor.fetchone()[0]
                st.write(row_id)

                cursor.execute("""
                INSERT INTO PRODUCTS (PRODUCT_ID, PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_DESCRIPTION, PRODUCT_TAGS, PRODUCT_IMAGE)
                VALUES (?, ?, ?, ?, ?, ?);""", (row_id, product_name, product_price, product_description, product_tags, image))
                connect.commit()


addProduct()
all_data = connect.execute("""SELECT * FROM BUSINESSES""")
for row in all_data:
    st.write(row)

all_data = connect.execute("""SELECT * FROM PRODUCTS""")
for row in all_data:
    st.write(row)


connect.close()