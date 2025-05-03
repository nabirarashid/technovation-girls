# Import libraries
import streamlit as st
import pandas as pd
import random
import sqlite3
from PIL import Image
import io

# Page setup
st.set_page_config(page_title="Get Image", page_icon="", layout="wide")

connect = sqlite3.connect("businesses.db")
cursor = connect.cursor()

# Randomly generating products
all_businesses = cursor.execute("""SELECT * FROM BUSINESSES""")
businesses = cursor.fetchone()

all_products = cursor.execute("""SELECT * FROM PRODUCTS
JOIN BUSINESSES ON PRODUCTS.business_id = BUSINESSES.id; """)

cursor.execute("""
SELECT PRODUCTS.PRODUCT_ID, PRODUCTS.PRODUCT_NAME, PRODUCTS.PRODUCT_PRICE, PRODUCTS.PRODUCT_DESCRIPTION, 
PRODUCTS.PRODUCT_TAGS, PRODUCTS.PRODUCT_IMAGE, BUSINESSES.business_name FROM PRODUCTS
JOIN BUSINESSES ON PRODUCTS.business_id = BUSINESSES.id
""" )

products = cursor.fetchone()


connect.close()

business_id, business_name = businesses
product_id, business_id, product_name, product_price, product_desc, product_tags, product_image = products


col1, col2 = st.columns(2)


with col1:
    # Show the image
    image = Image.open(io.BytesIO(product_image))
    st.image(image, width=500)

with col2:
    st.title(product_name)
    st.write(product_price)
    formatted_html = f"""
    <div style="font-family: 'Arial', sans-serif; padding: 8px 0;">
        <div style="font-size: 13px; color: #444;">{product_business}</div>
        <div style="font-size: 13px; color: #555;">{product_price}</div>
        <div style="font-size: 12px; color: #777;">
            {" | ".join(product_tags)}
        </div>
    </div>
    """

st.markdown(formatted_html, unsafe_allow_html=True)

