import streamlit as st
import pandas as pd
from streamlit_extras.stylable_container import stylable_container
from dotenv import load_dotenv
import os
import sqlite3

connect = sqlite3.connect("businesses.db")
cursor = connect.cursor()
all_products = cursor.execute("""SELECT PRODUCT_NAME, PRODUCT_IMAGE, BUSINESS_ID FROM PRODUCTS;""")


load_dotenv()

# Getting database

# Page setup
st.set_page_config(page_title="Home")

st.title("[Site Name]")

st.subheader("Welcome to [Site Name]! Start looking for products using the search bar, or browse below!")

# Search bar
text_search = st.text_input("Search for products:", value="")

# Query to search through
if text_search:
    query = """
        SELECT PRODUCT_NAME, PRODUCT_IMAGE, PRODUCT_PRICE, PRODUCT_DESCRIPTION, PRODUCT_TAGS, BUSINESS_ID
        FROM PRODUCTS
        JOIN BUSINESSES ON PRODUCTS.BUSINESS_ID = BUSINESSES.ID
        WHERE PRODUCT_NAME LIKE ? OR PRODUCT_TAGS LIKE ? OR NAME LIKE ?
    """
    search_term = f"%{text_search}%"  # Use wildcards for SQL LIKE query
    cursor.execute(query, (search_term, search_term, search_term))
    products = cursor.fetchall()

# Tags text
tags = ""


if text_search:
    for row_number, product in enumerate(products):
        if row_number % 3 == 0: # Every three rows, separate with a line
            st.write("---")
            cols = st.columns(3, gap="large")

        # Product info
        product_name, product_image, product_price, product_description, product_tags, business_id = product

        # Show product
        with cols[row_number%3]:
            # Tags text
            tags = " | ".join(product_tags.split(","))  # Assuming tags are comma-separated in the database

            cursor.execute("""SELECT NAME FROM BUSINESSES WHERE ID = ?""", (business_id,))
            business_name = cursor.fetchone()

            st.markdown(f"""
            <div style="background-color:#2ecc71;padding:20px;border-radius:10px;color:white;">
            <h3>{product_name} • ${product_price}</h3>
            <h6>Sold by {business_name}</h6>
            <h8>{id}</h8>
            <h9>{tags}</h9>

        </div>
    """, unsafe_allow_html=True)


# https://blog.streamlit.io/create-a-search-engine-with-streamlit-and-google-sheets/
# https://medium.com/@ericdennis7/how-to-beautify-streamlit-using-stylable-containers-69c1634971a6

connect.close()
