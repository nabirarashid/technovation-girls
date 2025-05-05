import streamlit as st
import os

st.set_page_config(
    page_title="HomeGrown",
    page_icon="🏬",
    layout="wide"
)

st.title("HomeGrown 🏬")

st.write("""
# Welcome to HomeGrown

Discover products from local businesses near you or add your own products to sell!
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Find Local Products")
    st.write("""
    Browse products from businesses near your location:
    
    - Search by distance (up to 50km)
    - Filter by product type or keywords
    - View product details and business information
    """)
    
    if st.button("🔍 Find Products", use_container_width=True):
        # Create pages directory if it doesn't exist
        os.makedirs("pages", exist_ok=True)
        
        # Navigate to the find products page
        st.switch_page("pages/find_products.py")

with col2:
    st.subheader("Add Your Products")
    st.write("""
    Are you a local business? Add your products to the marketplace:
    
    - Share details about your business and products
    - Upload product images
    - Add tags to make your products discoverable
    """)
    
    if st.button("➕ Add Products", use_container_width=True):
        # Create pages directory if it doesn't exist
        os.makedirs("pages", exist_ok=True)
        
        # Navigate to the add product page
        st.switch_page("pages/add_product.py")
