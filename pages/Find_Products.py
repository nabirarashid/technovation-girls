import streamlit as st
import random
import os
import sqlite3
from PIL import Image
import io

connect = sqlite3.connect("businesses.db")
cursor = connect.cursor()

# ID of product selected
product_chosen = 0

# Randomly generating products
all_products = cursor.execute("""SELECT PRODUCT_NAME, PRODUCT_IMAGE, ID FROM PRODUCTS;""")
products = cursor.fetchall()

if "shuffled_products" not in st.session_state:
    random.shuffle(products)
else:
    products = st.session_state.shuffled_products

for product in all_products:
    st.image(product)
# Show the dataframe
#st.write(df)

product_index = 0
product_selected = 0

import streamlit as st


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
            tile = st.container()
            with tile:
                st.markdown("<div style='margin-bottom: -15px'>", unsafe_allow_html=True)
                st.image(image)
                # Make a button users can click on, change this later
                button_pressed = st.button(product[0], key=f"btn_{product_index}")
                st.markdown("</div>", unsafe_allow_html=True)

                if button_pressed:
                    st.write(f"You clicked on: {product[0]}")
                    st.session_state["product_chosen"] = product[2]
                    st.session_state["product_selected"] = True
            
            product_index += 1


                


# Create a placeholder to control dynamic content
product_list_placeholder = st.empty()


# Displaying product
if 'product_chosen' in st.session_state and st.session_state.product_chosen is not None:
    selected_product_id = st.session_state.product_chosen
   
     # Get selected product info
    cursor.execute("""
            SELECT ID, BUSINESS_ID, PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_DESCRIPTION, PRODUCT_TAGS, PRODUCT_IMAGE
            FROM PRODUCTS WHERE ID = ?;
            """, (selected_product_id,))
    product_selected = cursor.fetchone()
    product_id, business_id, product_name, product_price, product_desc, product_tags, product_image = product_selected
    cursor.execute("""SELECT NAME FROM BUSINESSES WHERE ID = ?""", (selected_product_id,))
    business_selected = cursor.fetchone()
    if business_selected is not None:
        business_name = business_selected[0]
    else:
        st.error("No business found for the selected product.")
        business_name = "No business found"
    product_tags = product_tags.split(", ")



    if product_selected:

        col1, col2 = st.columns(2)


        with col1:
            # Show the image
            image = Image.open(io.BytesIO(product_image))
            st.image(image, width=500)

        with col2:
            st.title(product_name)
            st.subheader(f"{business_name} • ${product_price}")
            formatted_html = f"""
            <div style="font-family: 'Arial', sans-serif; padding: 8px 0;">
                <div style="font-size: 12px; color: #777;"> {" | ".join(product_tags)}</div>
            </div>
            """
            st.markdown(formatted_html, unsafe_allow_html=True)

            if st.button("Close"):
                st.session_state.product_chosen = None  # Reset the selected product
                st.reload()  # Reload the page to show the product list again
                st.switch_page("Find_Products.py")