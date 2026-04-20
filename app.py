import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(page_title="NYU Course API Test", page_icon="🏫")
st.title("🏫 NYU Course Data Fetching Test")
st.markdown("Test the previously found `POST` endpoint to verify if the data can be successfully fetched and parsed.")

# --- UI Interaction Area ---
# Provide an input box to dynamically test different course codes
course_alias = st.text_input("Please enter the course code you want to query (e.g., CSCI-UA 473):", value="ANST-UA 500")

# --- Core Fetching Logic ---
if st.button("🚀 Send Request and Fetch"):
    with st.spinner("Sending request to the NYU server..."):
        
        # 1. The API URL found previously
        url = "https://bulletins.nyu.edu/class-search/api/?page=fose&route=search"
        
        # 2. Mock request headers to simulate a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        
        # 3. Construct the request payload (dynamically passing the value from the input box)
        payload_data = {
            "other": {
                "srcdb": "9999"
            },
            "criteria": [
                {
                    "field": "alias",
                    "value": course_alias
                }
            ]
        }
        
        # 4. Send the request and handle the response
        try:
            response = requests.post(url, headers=headers, json=payload_data)
            
            if response.status_code == 200:
                st.success("🎉 Successfully fetched the response data!")
                
                # Parse the returned text as JSON
                course_data = response.json()
                
                # Streamlit has a dedicated component for rendering JSON, perfect for inspecting structures
                st.subheader("Raw JSON Structure Tree:")
                st.json(course_data)
                
            else:
                st.error(f"⚠️ Request failed, HTTP Status Code: {response.status_code}")
                st.text("Server response message:")
                st.text(response.text)
                
        except Exception as e:
            st.error(f"❌ A network request error occurred: {e}")