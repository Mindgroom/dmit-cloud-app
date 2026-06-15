import streamlit as st
import msal
import requests
import time

# --- 1. YOUR APP SETTINGS ---
CLIENT_ID = '88447086-851e-4712-bf2d-0747fa713fe6'
AUTHORITY = 'https://login.microsoftonline.com/consumers'
SCOPES = ['Files.ReadWrite.All']

st.set_page_config(page_title="Holistic Wellness Engine", layout="wide")
st.title("Holistic Wellness - DMIT Cloud Generator")

# --- 2. THE WEB DASHBOARD ---
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
        
    st.write("---")
    st.subheader("Fingerprint Data")
    
    col_atd1, col_atd2 = st.columns(2)
    with col_atd1:
        atd_left = st.number_input("ATD Angle Left", value=42)
    with col_atd2:
        atd_right = st.number_input("ATD Angle Right", value=41)

    patterns = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10", "W11", "L", "R", "A", "T"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Left Hand (L1-L5)**")
        l1_pat = st.selectbox("L1 Pattern", patterns, index=patterns.index("W5"))
        l1_rc = st.number_input("L1 RC", min_value=0, value=18)
        l2_pat = st.selectbox("L2 Pattern", patterns, index=patterns.index("W4"))
        l2_rc = st.number_input("L2 RC", min_value=0, value=13)
        l3_pat = st.selectbox("L3 Pattern", patterns, index=patterns.index("W2"))
        l3_rc = st.number_input("L3 RC", min_value=0, value=17)
        l4_pat = st.selectbox("L4 Pattern", patterns, index=patterns.index("W1"))
        l4_rc = st.number_input("L4 RC", min_value=0, value=19)
        l5_pat = st.selectbox("L5 Pattern", patterns, index=patterns.index("W9"))
        l5_rc = st.number_input("L5 RC", min_value=0, value=19)

    with col2:
        st.markdown("**Right Hand (R1-R5)**")
        r1_pat = st.selectbox("R1 Pattern", patterns, index=patterns.index("W5"))
        r1_rc = st.number_input("R1 RC", min_value=0, value=19)
        r2_pat = st.selectbox("R2 Pattern", patterns, index=patterns.index("L"))
        r2_rc = st.number_input("R2 RC", min_value=0, value=15)
        r3_pat = st.selectbox("R3 Pattern", patterns, index=patterns.index("L"))
        r3_rc = st.number_input("R3 RC", min_value=0, value=16)
        r4_pat = st.selectbox("R4 Pattern", patterns, index=patterns.index("W2"))
        r4_rc = st.number_input("R4 RC", min_value=0, value=23)
        r5_pat = st.selectbox("R5 Pattern", patterns, index=patterns.index("L"))
        r5_rc = st.number_input("R5 RC", min_value=0, value=20)

    submitted = st.form_submit_button("Generate Official Report")

# --- 3. THE CLOUD ENGINE CONNECTION ---
# --- 3. THE CLOUD ENGINE CONNECTION ---
if submitted:
    st.info("Initiating secure connection to Microsoft Cloud...")
    
    # Package the form data for Excel
    client_data = {
        'D5': [[client_name]], 'D7': [[parent_name]], 'D9': [[dob]], 
        'D11': [[mobile]], 'D13': [[email]], 'D15': [[address]], 
        'D19': [[atd_left]], 'D21': [[atd_right]],
        
        'D32': [[l1_pat]], 'D33': [[l1_rc]], 'D34': [[l2_pat]], 'D35': [[l2_rc]],
        'D36': [[l3_pat]], 'D37': [[l3_rc]], 'D38': [[l4_pat]], 'D39': [[l4_rc]],
        'D40': [[l5_pat]], 'D41': [[l5_rc]],
        
        'D42': [[r1_pat]], 'D43': [[r1_rc]], 'D44': [[r2_pat]], 'D45': [[r2_rc]],
        'D46': [[r3_pat]], 'D47': [[r3_rc]], 'D48': [[r4_pat]], 'D49': [[r4_rc]],
        'D50': [[r5_pat]], 'D51': [[r5_rc]],
    }

    try:
        app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
        
        # --- THE CLOUD-SAFE LOGIN METHOD ---
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" in flow:
            # Display the login instructions on the web dashboard
            st.warning(f"🔐 **Microsoft Security Check Required:**\n1. Click this link: {flow['verification_uri']}\n2. Enter this exact code: **{flow['user_code']}**")
            
            # The app will pause here and wait for you to type the code on Microsoft's website
            result = app.acquire_token_by_device_flow(flow)
            
            if "access_token" in result:
                headers = {'Authorization': 'Bearer ' + result['access_token'], 'Content-Type': 'application/json'}
                
                st.info("Injecting client data into the proprietary algorithm...")
                search_url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
                response = requests.get(search_url, headers=headers).json()
                file_id = next((f['id'] for f in response.get('value', []) if f['name'] == 'Rini Holistic Wellness.xlsx'), None)

                if file_id:
                    for cell, value in client_data.items():
                        update_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/workbook/worksheets('Input')/range(address='{cell}')"
                        requests.patch(update_url, headers=headers, json={"values": value})
                    
                    st.info("Processing 66-page layout... (This takes a few seconds)")
                    time.sleep(5) 
                    
                    pdf_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content?format=pdf"
                    pdf_response = requests.get(pdf_url, headers=headers)
                    
                    if pdf_response.status_code == 200:
                        st.success("Report generation complete!")
                        st.download_button(
                            label="Download PDF Report",
                            data=pdf_response.content,
                            file_name=f"{client_name.replace(' ', '_')}_Report.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("Failed to convert the file to PDF. Please try again.")
                else:
                    st.error("Could not find the Excel file in OneDrive.")
            else:
                st.error("Authentication failed or timed out.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
