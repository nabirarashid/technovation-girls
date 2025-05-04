import streamlit as st
import requests
import time

st.title("Geocoding Test")

address = st.text_input("Enter an address or postal code to test", "")

if st.button("Test Geocoding") and address:
    with st.spinner("Finding coordinates..."):
        # Add user-agent as it's required by Nominatim
        headers = {
            'User-Agent': 'LocalMarketplaceApp/1.0',
        }
        
        # Encode address for URL
        encoded_address = requests.utils.quote(address)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1"
        
        try:
            # Add a small delay to respect Nominatim usage policy
            time.sleep(1)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                st.success(f"Coordinates found: Latitude {lat}, Longitude {lon}")
                
                # Show additional information
                display_name = data[0].get('display_name', 'Location information not available')
                st.info(f"Location: {display_name}")
                
                # Create a map centered on the coordinates
                map_data = {'lat': [lat], 'lon': [lon]}
                st.map(map_data)
            else:
                st.warning(f"Could not find coordinates for: {address}")

        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            
        except (ValueError, KeyError) as e:
            st.error(f"Error processing location data: {e}")
