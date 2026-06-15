import streamlit as st
import msal
import requests
import time

# --- 1. SETTINGS ---
CLIENT_ID = '88447086-851e-4712-bf2d-0747fa713fe6'
AUTHORITY = 'https://login.microsoftonline.com/common'
SCOPES = ['Files.ReadWrite.All']

st.set_page_config(page_title="Mindgroom DMIT", layout="wide")
st.title("Mindgroom - DMIT Analysis System")

# --- 2. DATA MAPPINGS ---
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

# FILE ROUTER: Matches User Choice to Excel File
file_router = {
    "Upto 10th": "Report_Upto_10th.xlsx",
    "Science": "Report_Science.xlsx",
    "Commerce with Maths": "Report_Commerce_Maths.xlsx",
    "Commerce without Maths": "Report_Commerce_No_Maths.xlsx",
    "Humanities": "Report_Humanities.xlsx"
}

# --- 3. WEB DASHBOARD ---
with st.form("client_data_form"):
    
    st.subheader("Report Type")
    selected_stream = st.selectbox("Select the academic stream for this report:", list(file_router.keys()))
    
    st.write("---")
    st.subheader("Client Details")
    colA, colB, colC = st.columns(3)
    with colA:
        date_of_analysis = st.text_input("Date of Analysis", value="15-06-2026")
        client_name = st.text_input("Client Name", value="Aadya")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with colB:
        dob = st.text_input("Date of Birth", value="01-01-2010")
        mobile = st.text_input("Mobile No.", value="9876543210")
        email = st.text_input("Email Id", value="aadya@example.com")
    with colC:
        address = st.text_input("Address", value="New Delhi, India")
        parent_name = st.text_input("Parent Name", value="Parent")
        remarks = st.text_input("Remarks", value="None")
        
    st.write("---")
    st.subheader("Franchise & Analyst Details")
    col_F1, col_F2 = st.columns(2)
    with col_F1:
        analyst_id = st.text_input("Analyst Id", value="ANA-01")
        franchise_name = st.text_input("Franchise Name", value="Mindgroom Branch")
        franchise_company = st.text_input("Franchise Company", value="Mindgroom")
    with col_F2:
        franchise_contact = st.text_input("Franchise Contact", value="9876543210")
        franchise_address = st.text_input("Franchise Address", value="Delhi, India")
        
    st.write("---")
    st.subheader("Assign Fingerprint Patterns & RC Values")
    finger_labels = [
        "Left Thumb (L1)", "Left Index (L2)", "Left Middle (L3)", "Left Ring (L4)", "Left Little (L5)",
        "Right Thumb (L6)", "Right Index (L7)", "Right Middle (L8)", "Right Ring (L9)", "Right Little (L10)"
    ]
    
    col1, col2 = st.columns(2)
    finger_data = {} 
    
    for i, label in enumerate(finger_labels):
        with col1 if i < 5 else col2:
            st.markdown(f"**{label}**")
            selection = st.selectbox(f"Pattern", list(pattern_map.keys()), key=f"pat_{i}")
            rc_val = st.number_input(f"RC Count", min_value=0, value=15, key=f"rc_{i}")
            finger_data[label] = {"pattern": pattern_map[selection], "rc": rc_val}

    submitted = st.form_submit_button("Generate Official Report")

# --- 4. CLOUD ENGINE ---
if submitted:
    target_excel_file = file_router[selected_stream]
    st.info(f"Silently connecting to vault... Targeting: {target_excel_file}")
    
    # Exact mapping to the requested Excel cells
    client_data = {
        'E1': [[date_of_analysis]], 'D5': [[client_name]], 'D7': [[gender]], 
        'D9': [[dob]], 'D11': [[mobile]], 'D13': [[email]], 'D15': [[address]],
        'D17': [[parent_name]], 'D19': [[remarks]], 'D21': [[analyst_id]],
        'D23': [[franchise_name]], 'D25': [[franchise_company]], 
        'D27': [[franchise_contact]], 'D29': [[franchise_address]],
        
        # Left Hand (L1 - L5)
        'D32': [[finger_data["Left Thumb (L1)"]["pattern"]]], 'D33': [[finger_data["Left Thumb (L1)"]["rc"]]],
        'D34': [[finger_data["Left Index (L2)"]["pattern"]]], 'D35': [[finger_data["Left Index (L2)"]["rc"]]],
        'D36': [[finger_data["Left Middle (L3)"]["pattern"]]], 'D37': [[finger_data["Left Middle (L3)"]["rc"]]],
        'D38': [[finger_data["Left Ring (L4)"]["pattern"]]], 'D39': [[finger_data["Left Ring (L4)"]["rc"]]],
        'D40': [[finger_data["Left Little (L5)"]["pattern"]]], 'D41': [[finger_data["Left Little (L5)"]["rc"]]],
        
        # Right Hand (L6 - L10)
        'D42': [[finger_data["Right Thumb (L6)"]["pattern"]]], 'D43': [[finger_data["Right Thumb (L6)"]["rc"]]],
        'D44': [[finger_data["Right Index (L7)"]["pattern"]]], 'D45': [[finger_data["Right Index (L7)"]["rc"]]],
        'D46': [[finger_data["Right Middle (L8)"]["pattern"]]], 'D47': [[finger_data["Right Middle (L8)"]["rc"]]],
        'D48': [[finger_data["Right Ring (L9)"]["pattern"]]], 'D49': [[finger_data["Right Ring (L9)"]["rc"]]],
        'D50': [[finger_data["Right Little (L10)"]["pattern"]]], 'D51': [[finger_data["Right Little (L10)"]["rc"]]],
    }
