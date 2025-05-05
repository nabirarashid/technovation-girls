import streamlit as st
import sqlite3
import os
import requests
import math
import io
import random
import time
from PIL import Image
from dotenv import load_dotenv
from create_database import make_database
import base64

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
        # small delay to respect Nominatim usage policy
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


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on the earth (specified in decimal degrees)"""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371  # Radius of earth in kilometers
    distance_km = r * c
    
    return distance_km


@st.cache_data
def load_db_info():
    """Connect to database to get all results and store in cache"""
    with sqlite3.connect("businesses.db") as connect:
        cursor = connect.cursor()
        cursor.execute("""
            SELECT p.ID, p.BUSINESS_ID, p.PRODUCT_NAME, p.PRODUCT_PRICE, p.PRODUCT_DESCRIPTION, 
                p.PRODUCT_TAGS, p.PRODUCT_IMAGE,
                b.NAME as BUSINESS_NAME, b.LATITUDE, b.LONGITUDE
            FROM PRODUCTS p
            JOIN BUSINESSES b ON p.BUSINESS_ID = b.ID
            """)
        db_info = cursor.fetchall()
        return db_info


# Make database if it doesn't exist
make_database()

st.set_page_config(
    page_title="Find Local Products",
    page_icon="🔍",
    layout="wide",
)

st.title("Find Products Near You")

# Initialize session states
if "product_chosen" not in st.session_state:
    st.session_state.product_chosen = []

if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
    
if "user_lon" not in st.session_state:
    st.session_state.user_lon = None

if "user_location" not in st.session_state:
    st.session_state.user_location = ""

# User location input - in a sidebar
with st.sidebar:
    st.markdown("""
    <style>
    div.stForm {
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.form("Search by location"):
        st.subheader("Your Location")
        location_input_method = st.radio(
            "How would you like to provide your location?",
            ("Postal Code", "Address")
        )
        user_location = st.text_input(
            "Enter your " + ("postal code" if location_input_method == "Postal Code" else "address"),
            value=st.session_state.user_location,  # Set the default value from session state
            key="user_location"  # Bind to session state

        )
        search_term = st.text_input("Search for products by name, business or tags", ""),
        search_price = st.slider("Select the price range for products", 0, 200, (50, 100))
        search_radius = st.slider("Search radius (km)", 1, 50, 20)

        if st.form_submit_button("Search"):
            if not user_location:
                st.warning("Please enter your location to find nearby products.")
            else:
                # Geocode the user location
                user_lat, user_lon = geocode_address(user_location)
                
                if user_lat is None or user_lon is None:
                    st.error("Could not determine your location. Please enter a valid postal code or address.")
                else:
                    st.session_state.user_lat = user_lat
                    st.session_state.user_lon = user_lon
                    st.success(f"Your location found! Showing products within {search_radius} km.")
                    
                    # Clear any selected product when doing a new search
                    st.session_state.product_chosen = []
                    st.rerun()
        

# Main content area
content_placeholder = st.empty()

# Function to display product details
def display_product_details(product_id, container):
    db_info = load_db_info()
    product = next((p for p in db_info if p[0] == product_id), None)

    if not product:
        container.error("Product not found.")
        return

    product_id, business_id, name, price, description, tags, image_data, business_name, business_lat, business_lon = product
    tags_list = tags.split(", ") if tags else []

    with container:
        col1, col2 = st.columns(2)

        with col1:
            try:
                image = Image.open(io.BytesIO(image_data))
                st.image(image, width=500)
            except Exception as e:
                st.error(f"Error displaying image: {e}")

        with col2:
            st.title(name)
            
            # Calculate distance if user location is available
            distance_info = ""
            if st.session_state.user_lat and st.session_state.user_lon and business_lat and business_lon:
                distance = calculate_distance(
                    st.session_state.user_lat, st.session_state.user_lon, 
                    business_lat, business_lon
                )
                distance_info = f" • {distance:.1f} km away"
            
            st.subheader(f"{business_name}{distance_info} • ${price:.2f}")
            all_tags = ' | '.join(tags_list) 
            st.markdown(
                f"<div style='font-size: 12px; color: #777;'>{all_tags}</div>",
                unsafe_allow_html=True,
            )
            st.write(description)

            button_cols = st.columns([0.28, 0.72])
            with button_cols[0]:
                if st.button("Back to Products"):
                    if st.session_state.product_chosen:
                        st.session_state.product_chosen.pop()
                    container.empty()
                    st.rerun()
        
    st.markdown("<br>" * 5, unsafe_allow_html=True)
    st.subheader("Other people liked...")

    # Improved similar products logic
    similar_products = []
    for product in db_info:
        # Don't include the current product in similar products
        if product[0] != product_id:
            # Check if any tag is in the product's tags
            product_tags = product[5].split(", ") if product[5] else []
            tags_match = any(tag in product_tags for tag in tags_list)
            
            # Match by name, tags, or business name
            if (name.lower() in product[2].lower() or 
                tags_match or 
                business_name.lower() in product[7].lower()):
                similar_products.append(product)
    
    # Limit to a reasonable number of similar products
    similar_products = similar_products[:6]  # Show only 6 similar products max

    for row_number, product in enumerate(similar_products):
        s_id, s_business_id, s_name, s_price, s_description, s_tags, s_image, s_business_name, s_business_lat, s_business_lon = product

        if row_number % 3 == 0:  # Every three rows, create new columns
            cols = st.columns(3, gap="large")

        # Show product
        with cols[row_number % 3]:
            tile = st.container()

            with tile:                
                try:
                    st.image(s_image)
                except Exception as e:
                    st.error(f"Error displaying similar product image: {e}")
                        
                submitted = st.button(label="View", key=f"View_{s_id}", use_container_width=True)

                if submitted:
                    if len(st.session_state.product_chosen) == 0 or st.session_state.product_chosen[-1] != s_id:
                        st.session_state.product_chosen.append(s_id)
                    st.rerun()


# Main display logic
if st.session_state.product_chosen:
    # If a product is selected, display product details
    display_product_details(st.session_state.product_chosen[-1], content_placeholder)
else:
    # Display product grid based on location and search criteria
    with content_placeholder.container():
        if st.session_state.user_lat and st.session_state.user_lon:
            db_info = load_db_info()
            
            # Filter by search term if provided
            if search_term:
                search_term = search_term.lower()
                filtered_products = [
                    product for product in db_info
                    if (
                        search_term in product[2].lower() or  # name
                        search_term in (product[5].lower() if product[5] else "") or  # tags
                        search_term in product[7].lower()  # business name
                    )
                ]
            else:
                filtered_products = db_info
                
            # Filter by price if search button was clicked
            if  search_price:
                filtered_products = [
                    product for product in filtered_products
                    if search_price[0] <= product[3] <= search_price[1]  # price
                ]
                
            # Filter by distance and prepare for display
            nearby_products = []
            for product in filtered_products:
                product_id, business_id, name, price, description, tags, image_data, business_name, business_lat, business_lon = product
                
                if business_lat and business_lon:
                    try:
                        distance = calculate_distance(
                            st.session_state.user_lat, st.session_state.user_lon, 
                            business_lat, business_lon
                        )
                        if distance <= search_radius:
                            nearby_products.append((product_id, name, image_data, business_name, price, distance))
                    except Exception as e:
                        st.error(f"Error calculating distance: {e}")
            
            # Sort products by distance
            nearby_products.sort(key=lambda x: x[5])
            
            if not nearby_products:
                st.info(f"No related products found within {search_radius} km of your location.")
            else:
                st.subheader(f"Found {len(nearby_products)} products within {search_radius} km")
                
                # Display products in a grid
                product_index = 0
                num_rows = len(nearby_products) // 3 + (1 if len(nearby_products) % 3 else 0)

                for row in range(num_rows):
                    cols = st.columns(3)
                    for col in range(3):
                        if product_index >= len(nearby_products):
                            break

                        product_id, name, image_data, business_name, price, distance = nearby_products[product_index]

                        with cols[col]:
                            try:
                                image = Image.open(io.BytesIO(image_data))
                                st.image(image)
                                st.markdown(f"**{name}**")
                                st.caption(f"{business_name} • ${price:.2f} • {distance:.1f} km away")
                                if st.button("View Details", key=f"btn_{product_index}"):
                                    st.session_state.product_chosen.append(product_id)
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error displaying product: {e}")

                        product_index += 1
                                        
        else:
            st.info("Please enter your location in the sidebar to find products near you.")
            
            # Featured Products section - using direct database query for featured products
            try:
                with sqlite3.connect("businesses.db") as connect:
                    cursor = connect.cursor()
                    cursor.execute("""
                        SELECT p.ID, p.PRODUCT_NAME, p.PRODUCT_IMAGE, p.PRODUCT_PRICE, b.NAME as BUSINESS_NAME
                        FROM PRODUCTS p
                        JOIN BUSINESSES b ON p.BUSINESS_ID = b.ID
                    """)
                    products = cursor.fetchall()
                
                if products:
                    # Get random products for featured section
                    random_products = random.sample(products, min(10, len(products)))  

                    st.subheader("Featured Products You May Like 🌟")
                    product_index = 0
                    num_rows = len(random_products) // 3 + (1 if len(random_products) % 3 else 0)

                    for row in range(num_rows):
                        cols = st.columns(3)
                        for col in range(3):
                            if product_index >= len(random_products):
                                break

                            product_id, name, image_data, price, business_name = random_products[product_index]

                            with cols[col]:
                                try:
                                    image = Image.open(io.BytesIO(image_data))
                                    st.image(image)
                                    st.markdown(f"**{name}**")
                                    st.markdown(f"{business_name} • ${price:.2f}")
                                    if st.button("View Details", key=f"featured_{product_index}"):
                                        st.session_state.product_chosen.append(product_id)
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error displaying featured product: {e}")

                            product_index += 1
                else:
                    st.info("No products available in the database yet.")
                    
            except Exception as e:
                st.error(f"Error loading featured products: {e}")
