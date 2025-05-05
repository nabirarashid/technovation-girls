import streamlit as st
import time
from create_database import make_database
from dotenv import load_dotenv
import requests
import io
import os
import sqlite3
from PIL import Image

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

# Initialize session state variables
if "register_business" not in st.session_state:
    st.session_state.register_business = False
if "log_in" not in st.session_state:
    st.session_state.log_in = False
if 'add_product' not in st.session_state:
    st.session_state.add_product = False
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if "password_tried" not in st.session_state:
    st.session_state.password_tried = False
if "business_id" not in st.session_state:
    st.session_state.business_id = 0
if "business_name" not in st.session_state:
    st.session_state.business_name = ""

st.set_page_config(
    page_title="Add a Product",
    page_icon="",
)

business_screen = st.empty()

# Reset form fields if submitted
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
    
    # Choose to register a new business or log in
    cols = st.columns(2)
    with cols[0]:
        if st.button("Register a new business", use_container_width=True):
            st.session_state.register_business = True
    with cols[1]:
        if st.button("Log in", use_container_width=True):
            st.session_state.log_in = True

    # If user is logging in
    if st.session_state.log_in:
        st.session_state.register_business = False
        business_form = st.form("business_submission")

        with business_form:
            # Use context manager for database operations
            with sqlite3.connect("businesses.db") as connect:
                cursor = connect.cursor()
                cursor.execute("SELECT NAME, PASSWORD FROM BUSINESSES")
                all_businesses = cursor.fetchall()
                # Correct mapping of name to password
                business_info = {name: password for name, password in all_businesses}
                business_names = list(business_info.keys())
                        
            # Selecting business name
            business_name = st.selectbox("Choose business name", business_names)
            password = st.text_input("Enter your password:", type="password")

            submit = st.form_submit_button("Log in")
    
            if submit:
                if password == "":
                    st.error("Please enter a password!")
                elif password == business_info.get(business_name):
                    # Store business name and get business ID
                    st.session_state.business_name = business_name
                    
                    # Get business ID
                    with sqlite3.connect("businesses.db") as connect:
                        cursor = connect.cursor()
                        cursor.execute("SELECT ID FROM BUSINESSES WHERE NAME = ?", (business_name,))
                        business_id_result = cursor.fetchone()
                        if business_id_result:
                            st.session_state.business_id = business_id_result[0]
                    
                    st.success("Successfully logged in!")
                    st.session_state.add_product = True
                else:
                    st.error("Password is incorrect")
    
    # If user is registering a new business
    if st.session_state.register_business:
        st.session_state.log_in = False
        business_submission = st.form("add_business")

        with business_submission:
            business_name = business_submission.text_input("Business name: ")
            password = st.text_input("Create a password:", type="password")
            business_address = business_submission.text_input("Business Address:", 
                                                    help="Full address or postal code for location-based searches", 
                                                    key="business_address")
            submit = business_submission.form_submit_button("Add business!")

            if submit:
                if business_name == "" or password == "" or business_address == "":
                    st.error("Please fill in all fields!")
                else:
                    # Check if business already exists
                    with sqlite3.connect("businesses.db") as connect:
                        cursor = connect.cursor()
                        cursor.execute("SELECT * FROM BUSINESSES WHERE NAME = ?", (business_name,))
                        business_exists = cursor.fetchone()

                        if business_exists:
                            st.error("Business already exists!")
                        else:
                            lat, lon = geocode_address(business_address)
                            if lat is None:
                                st.error("Could not geocode this address. Please enter a valid address or postal code.")
                                return
                        
                            cursor.execute("INSERT INTO BUSINESSES (NAME, PASSWORD, LATITUDE, LONGITUDE) VALUES (?, ?, ?, ?);", 
                                          (business_name, password, lat, lon))
                            connect.commit()
                            cursor.execute("SELECT last_insert_rowid();")
                            st.session_state.business_id = cursor.fetchone()[0]
                            st.session_state.business_name = business_name
                            st.success("Business registered!")
                            st.session_state.add_product = True
                            st.session_state.register_business = False

    # If user is adding a product
    if st.session_state.add_product:
        product_form = st.form("product_submission")

        with product_form:
            st.write(f"Add a product for {st.session_state.business_name}!")
            
            product_name = product_form.text_input("Product name: ", key="product_name")
            product_price = product_form.number_input("Product price: ", key="product_price", min_value=0.0)
            product_description = product_form.text_input("Product description: ", key="product_description")
            product_tags = product_form.text_input("Please enter some tags to help people find your product, separated by commas: ", 
                                                key="product_tags")

            # Upload an image with error handling
            product_picture = product_form.file_uploader("Upload a picture of your product", 
                                                      type=['jpg', 'png'], 
                                                      accept_multiple_files=False)
            image = None
            if product_picture:
                try:
                    image = product_picture.read()
                    # Verify image is valid
                    Image.open(io.BytesIO(image))
                except Exception as e:
                    st.error(f"Error processing image: {e}")
                    image = None

            submit = st.form_submit_button('Add')

            # Updating database
            if submit:
                if product_name == "":
                    st.error("Please enter the name of your product!")
                elif not image:
                    st.error("Please upload a valid image of your product!")
                else:
                    business_id = st.session_state.business_id
                    
                    if business_id <= 0:
                        st.error("Business ID not found. Please log in again.")
                    else:
                        try:
                            with sqlite3.connect("businesses.db") as connect:
                                cursor = connect.cursor()
                                cursor.execute("""
                                INSERT INTO PRODUCTS (BUSINESS_ID, PRODUCT_NAME, PRODUCT_PRICE, 
                                                    PRODUCT_DESCRIPTION, PRODUCT_TAGS, PRODUCT_IMAGE)
                                VALUES (?, ?, ?, ?, ?, ?);""", 
                                              (business_id, product_name, product_price, 
                                               product_description, product_tags, image))
                                connect.commit()
                                st.success("Product submitted!")
                                st.session_state.submitted = True
                        except Exception as e:
                            st.error(f"Error adding product: {e}")

# Main function call
addProduct()

if st.checkbox("Show Database Content (Debug)", False):
    st.subheader("Registered Businesses")
    with sqlite3.connect("businesses.db") as connect:
        all_businesses = connect.execute("""SELECT * FROM BUSINESSES""")
        businesses_data = all_businesses.fetchall()
        for row in businesses_data:
            st.write(f"ID: {row[0]}, Name: {row[1]}, Latitude: {row[2]}, Longitude: {row[3]}")

    st.subheader("Registered Products")
    with sqlite3.connect("businesses.db") as connect:
        all_products = connect.execute("""SELECT * FROM PRODUCTS""")
        products_data = all_products.fetchall()
        for row in products_data:
            st.write(f"ID: {row[0]}, Business ID: {row[1]}, Name: {row[2]}, Price: ${row[3]:.2f}")
