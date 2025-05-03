import streamlit as st

col1, col2, col3 = st.columns(3)

with col1:
    for i in range(200,350,50):
        tile = st.container(height = i)
        with tile:
            st.image("133861178330852247.jpg", width= i)
        
with col2:
    for i in range(300,150,-50):
        tile = st.container(height = i)
        with tile:
            st.image("parrot.jpg", use_container_width="True")
            
with col3:
    for i in range(200,350,50):
        tile = st.container(height = i)
        with tile:
            st.image("133876857561662113.jpg", use_container_width="True")

