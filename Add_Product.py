import streamlit as st
import gspread
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import requests

st.set_page_config(
    page_title="Add a Product",
    page_icon="",
)

# Connecting to service account, sheets and drive
account = ""
gc = gspread.service_account(filename=account)
sh = gc.open("Technovation Database").sheet1

creds = service_account.Credentials.from_service_account_file(account, scopes=['https://www.googleapis.com/auth/drive'])
database = build('drive', 'v3', credentials=creds)


# Upload function
def upload_photo(file_name, file_bytes, folder_id=None):
    file_metadata = {'name': file_name}
    folder_id = ""
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype='image/jpeg')

    uploaded_file = database.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    # Make file public
    database.permissions().create(
        fileId=uploaded_file['id'],
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return uploaded_file.get('webViewLink')


# Checking if form has already been submitted
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

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
    
    # Making actual form
    product_form = st.form("product_submission")
    with product_form:
        st.write("Add a product!")

        # Basic business and product information
        business_name = product_form.text_input("Business name: ", key="business_name")
        product_name = product_form.text_input("Product name: ", key="product_name")
        product_price = product_form.number_input("Product price: ", key="product_price")
        product_description = product_form.text_input("Product description: ", key="product_description")
        product_tags = product_form.text_input("Please enter some tags to help people find your product, separated by commas: ", key="product_tags")

        # Upload an image
        product_pictures = product_form.file_uploader("Upload a picture of your product", type=['jpg', 'png'], accept_multiple_files=False)
        file_link = ""
        file_id = ""
        if product_pictures is not None:
            # Default image, change this default image
            file_bytes = product_pictures.read()
            file_link = upload_photo(product_pictures.name, file_bytes)
            id = file_link[32:]
            new_id = id.split("/view?usp=drivesdk")

            file_id = "https://drive.google.com/uc?export=view&id=" + new_id[0]

        submit = st.form_submit_button('Add')

        # Updating spreadsheet
        if submit:
            if product_name == "":
                st.error("Please enter the name of your product!")
            elif sh.find(product_name) != None:
                st.error("That product name already exists! Please add a different product name.")
            else:
                sh.append_row([business_name, product_name, product_price, product_description, product_tags, file_id])
                st.session_state.submitted = True
                st.success("Product added successfully!")
                #st.switch_page("streamlit_app.py")

    if product_pictures is not None:
        response = requests.get(file_id)
        st.image(response.content)


addProduct()


