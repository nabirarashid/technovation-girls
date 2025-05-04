import streamlit as st
import random
import sqlite3
from PIL import Image
import io
import base64

#cursor.execute("SELECT PRODUCT_NAME, PRODUCT_IMAGE, ID FROM PRODUCTS;")

default_query = "SELECT PRODUCT_NAME, PRODUCT_IMAGE, ID FROM PRODUCTS"
filters = []
filter_placeholder = st.empty()

content_placeholder = st.empty()


# I don't want to load this rn
def load_bg():
    with (open("sunset_bg_image.png", "rb") as image):
        data = image.read()
        bg_image = base64.b64encode(data).decode()

    # Setting background
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{bg_image}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

def set_bg_plain():
    # Changing background colour
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #fcefee;
    }
    </style>
    """, unsafe_allow_html=True)




# Filters
if len(st.session_state.get("product_chosen", [])) == 0:
    with filter_placeholder.container():

        # Price filter
        with st.form("filters"):
            filter_cols = st.columns(5)

            # Price dropdown menu
            with filter_cols[0]:
                price_filter = st.selectbox("Price", ("All", "Under $25", "$25 to $50", "$50 to $100", "$100 to $200", "$200 or more"))
            
            # Placeholder, add something else here
            with filter_cols[1]:
                product_type_filter = st.selectbox("Product Type", ("Clothing", "Food", "Furniture", "$25 to $50", "$50 to $100", "$100 to $200", "$200 or more"))

            # Placeholder, add something else here
            with filter_cols[2]:
                city_filter = st.selectbox("City", ("All", "Under $25", "$25 to $50", "$50 to $100", "$100 to $200", "$200 or more"))

            # Placeholder, add something else here
            with filter_cols[3]:
                search_bar = st.text_input("Search", value="")

            # Query to search through
            if search_bar:
                default_query = """
                    SELECT PRODUCT_NAME, PRODUCT_IMAGE, PRODUCTS.ID FROM PRODUCTS
                    JOIN BUSINESSES ON PRODUCTS.BUSINESS_ID = BUSINESSES.ID
                    WHERE PRODUCT_NAME LIKE ? OR PRODUCT_TAGS LIKE ? OR NAME LIKE ?
                """

            with filter_cols[4]:
                submitted = st.form_submit_button(label="Search")

            if submitted:
                # Price queries
                if product_type_filter == "Clothing":
                    filters.append("PRODUCT_PRICE < 25")
                elif product_type_filter == "Food":
                    filters.append("PRODUCT_PRICE <= 50 AND PRODUCT_PRICE >= 25")
                elif product_type_filter == "Furniture":
                    filters.append("PRODUCT_PRICE >= 100 AND PRODUCT_PRICE > 50")

                # Price queries
                if price_filter == "Under $25":
                    filters.append("PRODUCT_PRICE < 25")
                elif price_filter == "$25 to $50":
                    filters.append("PRODUCT_PRICE <= 50 AND PRODUCT_PRICE >= 25")
                elif price_filter == "$50 to $100":
                    filters.append("PRODUCT_PRICE >= 100 AND PRODUCT_PRICE > 50")
                elif price_filter == "$100 to $200":
                    filters.append("PRODUCT_PRICE <= 200 AND PRODUCT_PRICE > 100")
                elif price_filter == "$200 or more":
                    filters.append("PRODUCT_PRICE < 200")

        if filters:
                filter_clause = " WHERE " + " AND ".join(filters)
                query = default_query + filter_clause +  ";"
        else:
            query = default_query + ";"

        # popover

        with sqlite3.connect("businesses.db", check_same_thread=False) as connect:
            cursor = connect.cursor()
            if search_bar:
                cursor.execute(query, (search_bar.lower(), search_bar.lower(), search_bar.lower()))
            else:
                cursor.execute(query)
             
            products = cursor.fetchall()


        
        if len(products) > 0:

            # Shuffles products once per session
            if "shuffled_products" not in st.session_state or submitted:
                random.shuffle(products)
                st.session_state.shuffled_products = products

            # Always use the stored products list
            products = st.session_state.shuffled_products


        if products == []:
            st.error("We couldn't find any products with that query. Try choosing different filters.")


        elif "product_chosen" not in st.session_state:
            st.session_state.product_chosen = []



def display_product_details(product_id, container):
    with sqlite3.connect("businesses.db", check_same_thread=False) as connect:
        
        cursor = connect.cursor()
        cursor.execute(f"""
            SELECT ID, BUSINESS_ID, PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_DESCRIPTION, PRODUCT_TAGS, PRODUCT_IMAGE
            FROM PRODUCTS WHERE ID = ?;
        """, (product_id,))
        products = cursor.fetchone()
        product_id, business_id, name, price, description, all_tags, image_data = products

        cursor.execute("SELECT NAME FROM BUSINESSES WHERE ID = ?;", (business_id,))
        business = cursor.fetchone()

    if not products:
        container.error("Product not found.")
        return

    tags = all_tags.split(", ") if all_tags else []

    business_name = business[0] if business else "Unknown Business"

    if st.button("Back", use_container_width=True):
                st.session_state.product_chosen.pop()
                container.empty()
                st.rerun()

    if st.button("Return to scrolling page", use_container_width=True):
                st.session_state.product_chosen = []
                container.empty()
                st.rerun()

    with container:
        col1, col2 = st.columns(2)

        with col1:
            image = Image.open(io.BytesIO(image_data))
            st.image(image, width=500)

        with col2:
            st.markdown(f"""
                <div style="max-width: 500px; margin: auto;">
                    <h1 style="font-size: 32px;">{name}</h1>
                    <h3 style="font-size: 27px; color: #88669d;">Sold by {business_name} • ${price}</h3>
                    <p style="font-size: 16px; color: white; margin-top: 15px;">{description}</p>
                    <div style="font-size: 13px; color: white;">{" | ".join(tags)}</div>
                </div>
            """, unsafe_allow_html=True)









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
        with cols[row_number%3]:
            tile = st.container()
            # Tags text
            tags = " | ".join(all_tags.split(","))  # Assuming tags are comma-separated in the database

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











# BAD LOGIC --> actually it works!!
if len(st.session_state.product_chosen) == 0:
    with content_placeholder.container():
        

        # fake logic


        cols = st.columns(3)
        product_index = 0


        # main logic to display products in columns
        col1, col2, col3 = st.columns(3, gap="medium")


        for idx, product in enumerate(products):
            name, image_data, product_id = product
            col = cols[idx % 3]  # Rotate across columns 0 → 1 → 2


            with col:
                colour = "#bf9aca"
                image_base64 = base64.b64encode(image_data).decode("utf-8")
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
                </div>
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


                if st.button("View", key=f"main_{product_id}_{idx}", use_container_width=True):
                    st.session_state.product_chosen.append(product_id)
                    st.rerun()


else:
    if len(st.session_state.product_chosen) > 0:
        display_product_details(st.session_state.product_chosen[-1], content_placeholder)
