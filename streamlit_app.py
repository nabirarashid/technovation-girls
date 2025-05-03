import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from streamlit_extras.stylable_container import stylable_container
from dotenv import load_dotenv
import os

load_dotenv()

# Page setup
st.set_page_config(page_title="Home")

st.title("[Site Name]")

st.subheader("Welcome to [Site Name]! Start looking for products using the search bar, or browse below!")


# Connecting to service account, sheets and drive
url = os.environ["SPREADSHEET_URL"]
account = os.environ["ACCOUNT_JSON"]
gc = gspread.service_account(filename=account)
sh = gc.open("Technovation Database").sheet1
creds = service_account.Credentials.from_service_account_file(account, scopes=['https://www.googleapis.com/auth/drive'])
database = build('drive', 'v3', credentials=creds)
data = sh.get_all_records()
df = pd.DataFrame(data)

# Show the dataframe
#st.write(df)

# Search bar
text_search = st.text_input("Search for products:", value="")

# Filter the dataframe using masks
m1 = df["Business Name"].str.contains(text_search)
m2 = df["Product Name"].str.contains(text_search)
m3 = df["Product Tags"].str.contains(text_search)
df_search = df[m1 | m2 | m3]

# Tags text
tags = ""


if text_search:
    for row_number, row in df_search.reset_index().iterrows():
        if row_number % 3 == 0: # Every three rows, separate with a line
            st.write("---")
            cols = st.columns(3, gap="large")
        # Show product
        with cols[row_number%3]: # Show the product in first, second or third column
        # Tags text
            for i in row['Product Tags']:
                tags += i
            st.markdown(f"""
        <div style="background-color:#2ecc71;padding:20px;border-radius:10px;color:white;">
            <h3>{row['Product Name'].strip()} • ${str(row['Product Price']).strip()}</h3>
            <h6>Sold by {row['Business Name'].strip()}</h6>
            <h8>{row['Product Description'].strip()}</h8>
            <h9>{tags}</h9>

        </div>
    """, unsafe_allow_html=True)


# https://blog.streamlit.io/create-a-search-engine-with-streamlit-and-google-sheets/
# https://medium.com/@ericdennis7/how-to-beautify-streamlit-using-stylable-containers-69c1634971a6

# Becca's part!!
