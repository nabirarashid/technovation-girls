import streamlit as st
import sqlite3


# Page setup
st.set_page_config(page_title="Home")

st.title("HomeGrown")

st.subheader("Welcome to HomeGrown! Are you a Business or a Shopper?")

st.page_link("pages/Find_Products.py", label="Shopper")

st.page_link("pages/Add_Product.py", label="Business")

