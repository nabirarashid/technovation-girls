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
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
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

# Make database if it doesn't exist
make_database()

# Connect to the database
connect = sqlite3.connect("businesses.db")
cursor = connect.cursor()

st.set_page_config(
    page_title="Find Local Products",
    page_icon="🔍",
    layout="wide",
)

st.title("Find Products Near You")

# Initialize session states
if "product_chosen" not in st.session_state:
    st.session_state.product_chosen = None

if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
    
if "user_lon" not in st.session_state:
    st.session_state.user_lon = None

# User location input - in a sidebar
with st.sidebar:
    st.subheader("Your Location")
    location_input_method = st.radio(
        "How would you like to provide your location?",
        ("Postal Code", "Address")
    )

    user_location = st.text_input(
        "Enter your " + ("postal code" if location_input_method == "Postal Code" else "address")
    )

    search_radius = st.slider("Search radius (km)", 1, 50, 20)
    
    # Search by product tags or name
    st.subheader("Search Products")
    search_term = st.text_input("Search for products (name or tags)", "")
    search_price = st.slider("Select the price range for products", 5, 200, 50)
    
    if st.button("Find Products"):
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
                st.session_state.product_chosen = None
                st.rerun()

# Main content area
content_placeholder = st.empty()

# Function to display product details
def display_product_details(product_id, container, cursor):
    cursor.execute("""
        SELECT p.ID, p.BUSINESS_ID, p.PRODUCT_NAME, p.PRODUCT_PRICE, p.PRODUCT_DESCRIPTION, 
               p.PRODUCT_TAGS, p.PRODUCT_IMAGE,
               b.NAME as BUSINESS_NAME, b.LATITUDE, b.LONGITUDE
        FROM PRODUCTS p
        JOIN BUSINESSES b ON p.BUSINESS_ID = b.ID
        WHERE p.ID = ?;
    """, (product_id,))
    product = cursor.fetchone()

    if not product:
        container.error("Product not found.")
        return

    product_id, business_id, name, price, description, tags, image_data, business_name, business_lat, business_lon = product
    tags = tags.split(", ") if tags else []

    with container:
        col1, col2 = st.columns(2)

        with col1:
            image = Image.open(io.BytesIO(image_data))
            st.image(image, width=500)

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
            all_tags =  ' | '.join(tags) 
            st.markdown(
                f"<div style='font-size: 12px; color: #777;'> {all_tags}</div>",
                unsafe_allow_html=True,
            )
            st.write(description)

            if st.button("Back to Products"):
                st.session_state.product_chosen = None
                container.empty()
                st.rerun()
            
        

    st.write("Other people liked...") # maybe add filter here too

    with sqlite3.connect("businesses.db", check_same_thread=False) as connect:
        cursor = connect.cursor()
        cursor.execute("""
        SELECT PRODUCTS.ID, PRODUCT_NAME, PRODUCT_IMAGE, PRODUCT_PRICE, PRODUCT_DESCRIPTION, PRODUCT_TAGS, BUSINESS_ID
        FROM PRODUCTS
        JOIN BUSINESSES ON PRODUCTS.BUSINESS_ID = BUSINESSES.ID
        WHERE (PRODUCT_NAME LIKE ? OR PRODUCT_TAGS LIKE ? OR NAME LIKE ?) AND PRODUCTS.ID != ?
        """, (name, all_tags, business_name, product_id))
        similar_products = cursor.fetchall()

    for row_number, product in enumerate(similar_products):

        s_id, s_name, s_image, s_price, s_desc, s_tags, s_business_id = product

        if row_number % 3 == 0: # Every three rows, separate with a line
            cols = st.columns(3, gap="large")

        # Show product
        # STARTS HERE!!!!
        with cols[row_number%3]:
            tile = st.container()
            # Tags text

            image_base64 = base64.b64encode(s_image).decode("utf-8")

            with tile:
                colour = "#bf9aca"
                st.markdown(f"""
                        <div style="
                    border-radius: 10px;
                    background-color: {colour};
                    padding: 15px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    text-align: center;
                    color: white;
                    margin-bottom: -50px;
                ">
                    <img src="data:image/png;base64,{image_base64}" style="width: 100%; border-radius: 8px;" />
                    <div style="font-size: 25px; font-weight: bold; margin-top: 10px; margin-bottom: 10px;">{name}</div>
                </div></style>
                    """, unsafe_allow_html=True)

                st.markdown("""
                <style>
                button[kind="secondary"] {
                    background-color: """ + colour + """};
                    color: white;
                    border-radius: 10px;
                    font-weight: bold;
                    transition: background-color 0.3s ease;
                    border-top: -20px;
                }


                button[kind="secondary"]:hover {
                    background-color: #white;
                }
                </style>
            """, unsafe_allow_html=True)

                    
            submitted = st.button(label="View", key=f"View_{s_id}", use_container_width=True)

            if submitted:
                    if st.session_state.product_chosen[-1] != s_id:
                        st.session_state.product_chosen.append(s_id)
                    st.rerun()





# Main display logic
if st.session_state.product_chosen is not None:
    # Display the selected product details
    display_product_details(st.session_state.product_chosen, content_placeholder, cursor)
else:
    # Display product grid based on location and search criteria
    with content_placeholder.container():
        if st.session_state.user_lat and st.session_state.user_lon:
            # Get all businesses with their coordinates
            if search_term:
                cursor.execute("""
                    SELECT p.ID, p.PRODUCT_NAME, p.PRODUCT_IMAGE, b.LATITUDE, b.LONGITUDE, p.PRODUCT_PRICE, b.NAME as BUSINESS_NAME
                    FROM PRODUCTS p
                    JOIN BUSINESSES b ON p.BUSINESS_ID = b.ID
                    WHERE p.PRODUCT_NAME LIKE ? OR p.PRODUCT_TAGS LIKE ? OR p.PRODUCT_DESCRIPTION LIKE ?
                """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("""
                    SELECT p.ID, p.PRODUCT_NAME, p.PRODUCT_IMAGE, b.LATITUDE, b.LONGITUDE, p.PRODUCT_PRICE, b.NAME as BUSINESS_NAME
                    FROM PRODUCTS p
                    JOIN BUSINESSES b ON p.BUSINESS_ID = b.ID
                """)
            
            products = cursor.fetchall()
            
            # Filter products by distance
            nearby_products = []
            for product in products:
                product_id, name, image_data, business_lat, business_lon, price, business_name = product
                if business_lat and business_lon:
                    distance = calculate_distance(
                        st.session_state.user_lat, st.session_state.user_lon, 
                        business_lat, business_lon
                    )
                    if distance <= search_radius and search_price + 15 >= price and search_price - 15 <= price:
                        nearby_products.append((product_id, name, image_data, business_name, distance))
            
            # Sort products by distance
            nearby_products.sort(key=lambda x: x[4])  # Sort by the distance (5th element)
            
            if not nearby_products:
                st.info(f"No products found within {search_radius} km of your location.")
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

                        product_id, name, image_data, business_name, distance = nearby_products[product_index]

                        with cols[col]:
                            image = Image.open(io.BytesIO(image_data))
                            st.image(image)
                            st.markdown(f"**{name}**")
                            st.caption(f"{business_name} • {distance:.1f} km away")
                            if st.button("View Details", key=f"btn_{product_index}"):
                                st.session_state.product_chosen = product_id
                                st.rerun()
                            

                        product_index += 1
        else:
            st.info("Please enter your location in the sidebar to find products near you.")

            # featured products
            cursor.execute("""
                SELECT p.ID, p.PRODUCT_NAME, p.PRODUCT_IMAGE, p.PRODUCT_PRICE, b.NAME as BUSINESS_NAME
                FROM PRODUCTS p
                JOIN BUSINESSES b ON p.BUSINESS_ID = b.ID
            """)
            products = cursor.fetchall()
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
                            image = Image.open(io.BytesIO(image_data))
                            st.image(image)
                            st.markdown(f"**{name}**")
                            st.markdown(f"{business_name} • ${price:.2f}")
                            if st.button("View Details", key=f"btn_{product_index}"):
                                st.session_state.product_chosen = product_id
                                st.rerun()

                        product_index += 1



connect.close()
