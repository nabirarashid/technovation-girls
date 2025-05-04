import streamlit as st
import io
import os
from create_database import make_database
import sqlite3

connect = sqlite3.connect("businesses.db")
cursor = connect.cursor()

if "register_business" not in st.session_state:
    st.session_state.register_business = False
if "log_in" not in st.session_state:
    st.session_state.log_in = False
if 'add_product' not in st.session_state:
    st.session_state.add_product = False
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
st.session_state.password_tried = False
if "business_id" not in st.session_state:
    st.session_state.business_id = 0

st.set_page_config(
    page_title="Add a Product",
    page_icon="",
)

# Make database
make_database()

business_screen = st.empty()





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
        password = ""
        business_form = st.form("business_submission")

        with business_form:
            cursor.execute("SELECT NAME, PASSWORD FROM BUSINESSES")
            all_businesses = cursor.fetchall()
            business_info = {name: id for id, name in all_businesses}
            business_names = list(business_info.keys())
                        
            # Selecting business name
            password = "Enter a password"
            business_name = st.selectbox("Choose business name", business_names)
            password = st.text_input("Enter your password:")

            submit = st.form_submit_button("Log in")

            

    
            if submit:
                if password == "":
                    st.write("AAFEJSNOIS")
                    st.error("Please enter a password!")
                elif password == business_info.get(business_name):
                    st.success("Successfully logged in!")
                    st.session_state.add_product = True
                else:
                    st.error("Password is incorrect")
                

    
    if st.session_state.register_business:
        st.session_state.log_in = False
        business_submission = st.form("add_business")

        with business_submission:
            business_name = business_submission.text_input("Business name: ")
            password = st.text_input("Create a password:")
            submit = business_submission.form_submit_button("Add business!")

            if submit:
                if business_name == "" or password == "":
                    st.error("Please fill in all fields!")
                else:
                    cursor.execute("SELECT * FROM BUSINESSES WHERE NAME = ?", (business_name,))
                    business_exists = cursor.fetchone()

                    if business_exists:
                        st.error("Business already exists!")
                    else:
                        cursor.execute("INSERT INTO BUSINESSES (NAME, PASSWORD) VALUES (?, ?);", (business_name, password))
                        connect.commit()
                        cursor.execute("SELECT last_insert_rowid();")
                        st.session_state.business_id = cursor.fetchone()[0]
                        st.success("Business registered!")
                        st.session_state.add_product = True
                        st.session_state.register_business = False
            



    if st.session_state.add_product:
        product_form = st.form("product_submission")

        with product_form:
            st.write("Add a product!")
            

        with product_form:
            product_name = product_form.text_input("Product name: ", key="product_name")
            product_price = product_form.number_input("Product price: ", key="product_price")
            product_description = product_form.text_input("Product description: ", key="product_description")
            product_tags = product_form.text_input("Please enter some tags to help people find your product, separated by commas: ", key="product_tags")

            # Upload an image
            product_picture = product_form.file_uploader("Upload a picture of your product", type=['jpg', 'png'], accept_multiple_files=False)
            if product_picture:
                image = product_picture.read()     

            submit = st.form_submit_button('Add')


            # Updating database
            if submit:
                if product_name == "":
                    st.error("Please enter the name of your product!")
                elif not product_picture:
                    st.error("Please upload an image of your product!")
                else:
                    # Inserting business name into database if it doesn't exist
                    cursor.execute("SELECT ID FROM BUSINESSES WHERE NAME = ?", (business_name,))
                    business_id_query = cursor.fetchone()

                    cursor.execute("""
                    INSERT INTO PRODUCTS (BUSINESS_ID, PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_DESCRIPTION, PRODUCT_TAGS, PRODUCT_IMAGE)
                    VALUES (?, ?, ?, ?, ?, ?);""", (st.session_state.business_id, product_name, product_price, product_description, product_tags, image))
                    connect.commit()
                    st.success("Product submitted!")


addProduct()

connect.close()

