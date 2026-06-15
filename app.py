import streamlit as st
import msal
import requests
import time
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. SETTINGS ---
CLIENT_ID = '88447086-851e-4712-bf2d-0747fa713fe6'
AUTHORITY = 'https://login.microsoftonline.com/common'
SCOPES = ['Files.ReadWrite.All']

st.set_page_config(page_title="Mindgroom DMIT", layout="wide")

# --- 2. GOOGLE SHEETS AUTHENTICATION ---
def get_gspread_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    return gspread.authorize(creds)

# --- 3. SESSION STATE LOGIC ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.access_code = ""
    st.session_state.franchise_name = ""
    st.session_state.credits = 0

# --- 4. THE LOGIN GATE ---
if not st.session_state.logged_in:
    st.title("Mindgroom - Partner Portal")
    st.info("Please enter your Franchise Access Code to continue.")
    
    with st.form("login_form"):
        code_input = st.text_input("Access Code", type="password")
        login_submitted = st.form_submit_button("Login")
        
        if login_submitted:
            try:
                gc = get_gspread_client()
                sh = gc.open("Mindgroom_DB")
                worksheet = sh.worksheet("Franchise_Credits")
                
                # Fetch all data to find the user
                records = worksheet.get_all_records()
                user_record = next((item for item in records if str(item["Access_Code"]) == code_input), None)
                
                if user_record:
                    if int(user_record["Credits"]) > 0:
                        st.session_state.logged_in = True
                        st.session_state.access_code = code_input
                        st.session_state.franchise_name = user_record["Franchise_Name"]
                        st.session_state.credits = int(user_record["Credits"])
                        st.rerun()
                    else:
                        st.error("Access Denied: 0 Credits Remaining. Please contact Mindgroom Admin to recharge.")
                else:
                    st.error("Invalid Access Code. Please try again.")
            except Exception as e:
                st.error(f"Database Error: Could not connect to the credential server. {e}")

# --- 5. THE MAIN DASHBOARD (Only visible if logged in) ---
else:
    st.title("Mindgroom - DMIT Analysis System")
    
    # Show active credits in the UI
    st.success(f"Welcome, **{st.session_state.franchise_name}** | Credits Available: **{st.session_state.credits}**")
    
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

    file_router = {
        "Upto 10th": "Report_Upto_10th.xlsx",
        "Science": "Report_Science.xlsx",
        "Commerce with Maths": "Report_Commerce_Maths.xlsx",
        "Commerce without Maths": "Report_Commerce_No_Maths.xlsx",
        "Humanities": "Report_Humanities.xlsx"
    }

    with st.form("client_data_form"):
        st.subheader("Report Type")
        selected_stream = st.selectbox("Select the academic stream for this report:", list(file_router.keys()))
        
        st.write("---")
        st.subheader("Client Details")
        colA, colB, colC = st.columns(3)
        with colA:
            date_of_analysis = st.text_input("Date of Analysis", value=datetime.today().strftime('%d-%m-%Y'))
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
        st.subheader("Franchise Details")
        col_F1, col_F2 = st.columns(2)
        with col_F1:
            analyst_id = st.text_input("Analyst Id", value=st.session_state.access_code)
            franchise_name = st.text_input("Franchise Name", value=st.session_state.franchise_name)
            franchise_company = st.text_input("Franchise Company", value=st.session_state.franchise_name)
        with col_F2:
            franchise_contact = st.text_input("Franchise Contact", value="Update Contact")
            franchise_address = st.text_input("Franchise Address", value="Update Address")
            
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

        # THIS IS THE BUTTON THAT WAS MISSING!
        submitted = st.form_submit_button("Generate Report (Deducts 1 Credit)")

    # --- 6. CLOUD ENGINE & LEDGER UPDATE ---
    if submitted:
        target_excel_file = file_router[selected_stream]
        st.info(f"Connecting to Master Vault... Targeting: {target_excel_file}")
        
        client_data = {
            'E1': [[date_of_analysis]], 'D5': [[client_name]], 'D7': [[gender]], 
            'D9': [[dob]], 'D11': [[mobile]], 'D13': [[email]], 'D15': [[address]],
            'D17': [[parent_name]], 'D19': [[remarks]], 'D21': [[analyst_id]],
            'D23': [[franchise_name]], 'D25': [[franchise_company]], 
            'D27': [[franchise_contact]], 'D29': [[franchise_address]],
            'D32': [[finger_data["Left Thumb
