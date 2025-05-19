
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Medical Assistant",
    page_icon="🩺",
    layout="wide"
)

# Initialization
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""

# Simple user database
users = {
    "doctor1": "password123",
    "doctor2": "password456"
}

# Login page
def login_page():
    st.title("Medical Assistant Login")
    
    st.markdown("### Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Simple response function
def get_medical_response(query):
    if "diabetes" in query.lower():
        return "Here's information about diabetes management based on current guidelines: The ADA's Standards of Medical Care recommends individualized A1C targets, typically <7% for most patients. First-line therapy remains metformin for most patients with Type 2 diabetes. GLP-1 receptor agonists and SGLT-2 inhibitors are recommended for patients with cardiovascular disease."
    elif "hypertension" in query.lower():
        return "Regarding hypertension management, current guidelines recommend: Target BP <130/80 mmHg for most patients according to ACC/AHA guidelines. First-line treatments include thiazide diuretics, ACE inhibitors, ARBs, and CCBs. Lifestyle modifications remain foundational (DASH diet, sodium restriction, physical activity)."
    else:
        return "Thank you for your medical query. As an AI medical assistant, I can provide general information based on medical literature, but clinical judgment is essential. For more specific guidance, additional clinical details would be helpful."

# Main application
def main_app():
    st.title(f"Medical Assistant - Welcome, {st.session_state.username}")
    
    # Disclaimer
    st.warning("**Important:** This tool is for healthcare professionals only. All AI-generated responses should be reviewed by qualified medical personnel. Not intended for direct patient use.")
    
    # Sidebar
    with st.sidebar:
        st.header("Options")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.messages = []
            st.experimental_rerun()
        
        st.header("Prescription Analysis")
        st.file_uploader("Upload a prescription", type=["jpg", "jpeg", "png", "pdf"])
        
        if st.button("Analyze Prescription"):
            st.info("In the full version, this would analyze the prescription using Palmyra-Med-70B-32K.")
            st.session_state.messages.append({"role": "user", "content": "Analyzed prescription"})
            st.session_state.messages.append({"role": "assistant", "content": "Prescription Analysis Results: This feature will analyze medication names, dosages, potential interactions, and other relevant information."})
            st.experimental_rerun()
    
    # Chat interface
    st.header("Medical Chat Assistant")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.info(message["content"])
        else:
            st.success(message["content"])
    
    # User input
    user_input = st.text_input("Type your medical question here...")
    
    if st.button("Send"):
        if user_input:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get and display response
            response = get_medical_response(user_input)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.experimental_rerun()

# Main logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
