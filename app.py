import streamlit as st
import msal
import requests
import time

# --- 1. SETTINGS ---
CLIENT_ID = '88447086-851e-4712-bf2d-0747fa713fe6'
AUTHORITY = 'https://login.microsoftonline.com/common'
SCOPES = ['Files.ReadWrite.All']

st.set_page_config(page_title="Mindgroom DMIT", layout="wide")
st.title("Mindgroom - DMIT Report Generation")

# --- 2. PATTERN MAPPING ---
pattern_map = {
    "Target Centric": "W1", "Spiral": "W2", "Elongated Target Centric": "W3",
    "Elongated Spiral": "W4", "Double Loop": "W5", "Imploding": "W6",
    "Composite": "W7", "Target Centric Ulnar Peacock's Eye": "W8",
    "Spiral Ulnar Peacock's Eye": "W9", "Target Centric Radial Peacock's Eye": "W10",
    "Spiral Radial Peacock's Eye": "W11", "Ulnar Loop": "L", "Radial Loop": "R",
    "Ulnar Falling Loop": "L1", "Radial Falling Loop": "R1", "Plain Arch": "X1",
    "Tented Arch": "X2", "Tented Arch with Ulnar Loop": "X3",
    "Tented Arch with Radial Loop": "X4", "Accidental Whorl": "W"
}

# --- 3. WEB DASHBOARD ---
with st.form("client_data_form"):
    st.subheader("Client Details")
    colA, colB, colC = st.columns(3)
    with colA:
        client_name = st.text_input("Client Name", value="Aadya")
        parent_name = st.text_input("Parent's Name", value="Parent")
    with colB:
        dob = st.text_input("Date of Birth", value="01-01-2010")
        mobile = st.text_input("Mobile No.", value="9876543210")
    with colC:
        email = st.text_input("Email", value="aadya@example.com")
        address = st.text_input("Address", value="New Delhi, India")
        
    st.subheader("Assign Fingerprint Patterns & RC Values")
    finger_labels = [
        "Left Thumb", "Left Index", "Left Middle", "Left Ring", "Left Little",
        "Right Thumb", "Right Index", "Right Middle", "Right Ring", "Right Little"
    ]
    
    col1, col2 = st.columns(2)
    finger_data = {} 
    
    for i, label in enumerate(finger_labels):
        with col1 if i < 5 else col2:
            st.markdown(f"**{label}**")
            selection = st.selectbox(f"Pattern", list(pattern_map.keys()), key=f"pat_{i}")
            rc_val = st.number_input(f"RC Value", min_value=0, value=15, key=f"rc_{i}")
            finger_data[label] = {"pattern": pattern_map[selection], "rc": rc_val}

    submitted = st.form_submit_button("Generate Official Report")

# --- 4. CLOUD ENGINE ---
if submitted:
    st.info("Silently connecting to the secure vault...")
    
    client_data = {
        'D5': [[client_name]], 'D7': [[parent_name]], 'D9': [[dob]], 
        'D11': [[mobile]], 'D13': [[email]], 'D15': [[address]], 
        'D32': [[finger_data["Left Thumb"]["pattern"]]], 'D33': [[finger_data["Left Thumb"]["rc"]]],
        'D34': [[finger_data["Left Index"]["pattern"]]], 'D35': [[finger_data["Left Index"]["rc"]]],
        'D36': [[finger_data["Left Middle"]["pattern"]]], 'D37': [[finger_data["Left Middle"]["rc"]]],
        'D38': [[finger_data["Left Ring"]["pattern"]]], 'D39': [[finger_data["Left Ring"]["rc"]]],
        'D40': [[finger_data["Left Little"]["pattern"]]], 'D41': [[finger_data["Left Little"]["rc"]]],
        'D42': [[finger_data["Right Thumb"]["pattern"]]], 'D43': [[finger_data["Right Thumb"]["rc"]]],
        'D44': [[finger_data["Right Index"]["pattern"]]], 'D45': [[finger_data["Right Index"]["rc"]]],
        'D46': [[finger_data["Right Middle"]["pattern"]]], 'D47': [[finger_data["Right Middle"]["rc"]]],
        'D48': [[finger_data["Right Ring"]["pattern"]]], 'D49': [[finger_data["Right Ring"]["rc"]]],
        'D50': [[finger_data["Right Little"]["pattern"]]], 'D51': [[finger_data["Right Little"]["rc"]]],
    }

    try:
        app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
        result = app.acquire_token_by_refresh_token(st.secrets["MS_REFRESH_TOKEN"], scopes=SCOPES)
        
        if "access_token" in result:
            headers = {'Authorization': 'Bearer ' + result['access_token'], 'Content-Type': 'application/json'}
            search_url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
            response = requests.get(search_url, headers=headers).json()
            file_id = next((f['id'] for f in response.get('value', []) if f['name'] == 'Rini Holistic Wellness.xlsx'), None)

            if file_id:
                for cell, value in client_data.items():
                    requests.patch(f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/workbook/worksheets('Input')/range(address='{cell}')", 
                                   headers=headers, json={"values": value})
                
                st.info("Processing layout...")
                time.sleep(5) 
                pdf = requests.get(f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content?format=pdf", headers=headers)
                st.download_button("Download PDF Report", data=pdf.content, file_name="Report.pdf", mime="application/pdf")
            else:
                st.error("Excel file not found.")
        else:
            st.error("System security override failed.")
    except Exception as e:
        st.error(f"Error: {e}")
