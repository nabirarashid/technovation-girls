import streamlit as st
import io
import os
import time
from create_database import make_database
import sqlite3
from dotenv import load_dotenv
import requests
import math

# Load environment variables (not required for Nominatim but keeping for future use)
load_dotenv()

def geocode_address(address):
    """Convert an address to latitude and longitude using Nominatim (OpenStreetMap)"""
    # Add user-agent as it's required by Nominatim
    headers = {
        'User-Agent': 'LocalMarketplaceApp/1.0',
    }
    
    # Encode address for URL
    encoded_address = requests.utils.quote(address)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1"
    
    try:
        # Add a small delay to respect Nominatim usage policy
        time.sleep(1)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            st.warning(f"Could not find coordinates for: {address}")
            return None, None

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None, None

    except (ValueError, KeyError) as e:
        st.error(f"Error processing location data: {e}")
        return None, None

# Make database
make_database()

connect = sqlite3.connect("businesses.db")
cursor = connect.cursor()

st.set_page_config(
    page_title="Add a Product",
    page_icon="➕",
    layout="wide",
)

st.title("Add Your Product")

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
    col1, col2 = st.columns([2, 1])
    
    with col1:
        product_form = st.form("product_submission")
        with product_form:
            st.subheader("Add a new product to the marketplace")

            # Business information
            st.write("### Business Information")
            business_name = product_form.text_input("Business name:", key="business_name")
            business_address = product_form.text_input("Business Address:", 
                                                    help="Full address or postal code for location-based searches", 
                                                    key="business_address")
            
            # Product information
            st.write("### Product Details")
            product_name = product_form.text_input("Product name:", key="product_name")
            product_price = product_form.number_input("Product price ($):", 
                                                    min_value=0.0, 
                                                    format="%.2f", 
                                                    key="product_price")
            product_description = product_form.text_area("Product description:", 
                                                        height=100, 
                                                        key="product_description")
            product_tags = product_form.text_input("Tags (separated by commas):", 
                                                help="Enter keywords to help customers find your product", 
                                                key="product_tags")

            # Upload an image
            st.write("### Product Image")
            product_picture = product_form.file_uploader("Upload a picture of your product", 
                                                        type=['jpg', 'jpeg', 'png'], 
                                                        accept_multiple_files=False)
            
            submit = st.form_submit_button('Add Product')

            # Updating database
            if submit:
                if not business_name:
                    st.error("Please enter your business name!")
                elif not business_address:
                    st.error("Please enter your business address or postal code!")
                elif not product_name:
                    st.error("Please enter the name of your product!")
                elif not product_picture:
                    st.error("Please upload an image of your product!")
                else:
                    # Handle image
                    image = product_picture.read()
                    
                    # Check if business exists
                    cursor.execute("SELECT ID, LATITUDE, LONGITUDE FROM BUSINESSES WHERE NAME = ?", (business_name,))
                    business_record = cursor.fetchone()

                    if business_record:
                        business_id = business_record[0]
                        # If business exists but doesn't have coordinates, update them
                        if business_record[1] is None or business_record[2] is None:
                            lat, lon = geocode_address(business_address)
                            if lat is None:
                                st.error("Could not geocode this address. Please enter a valid address or postal code.")
                                return
                            cursor.execute(
                                "UPDATE BUSINESSES SET LATITUDE = ?, LONGITUDE = ? WHERE ID = ?",
                                (lat, lon, business_id)
                            )
                    else:
                        # Create new business with coordinates
                        lat, lon = geocode_address(business_address)
                        if lat is None:
                            st.error("Could not geocode this address. Please enter a valid address or postal code.")
                            return
                        
                        cursor.execute(
                            "INSERT INTO BUSINESSES (NAME, LATITUDE, LONGITUDE) VALUES (?, ?, ?);",
                            (business_name, lat, lon)
                        )
                        cursor.execute("SELECT last_insert_rowid();")
                        business_id = cursor.fetchone()[0]

                    # Add product
                    cursor.execute("""
                        INSERT INTO PRODUCTS (
                            BUSINESS_ID, PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_DESCRIPTION,
                            PRODUCT_TAGS, PRODUCT_IMAGE
                        ) VALUES (?, ?, ?, ?, ?, ?);
                    """, (business_id, product_name, product_price, product_description, product_tags, image))
                    connect.commit()
                    st.success("Product added successfully!")
                    st.session_state.submitted = True

    with col2:
        st.markdown("""
        ### Tips for Adding Products
        
        - Use a clear, high-quality image 
        - Provide a detailed description
        - Add relevant tags to help customers find your product
        - Make sure your business address is accurate for local search
        - Set a competitive price
        
        Your products will be shown to customers within their selected search radius based on your business location.
        """)

addProduct()

# Optional debug section (can be commented out in production)
if st.checkbox("Show Database Content (Debug)", False):
    st.subheader("Registered Businesses")
    all_businesses = connect.execute("""SELECT * FROM BUSINESSES""")
    businesses_data = all_businesses.fetchall()
    for row in businesses_data:
        st.write(f"ID: {row[0]}, Name: {row[1]}, Latitude: {row[2]}, Longitude: {row[3]}")

    st.subheader("Registered Products")
    all_products = connect.execute("""SELECT * FROM PRODUCTS""")
    products_data = all_products.fetchall()
    for row in products_data:
        st.write(f"ID: {row[0]}, Business ID: {row[1]}, Name: {row[2]}, Price: ${row[3]:.2f}")

connect.close()
