import streamlit as st
import requests
import json

# Set page configuration
st.set_page_config(
    page_title="Dr. Daya Shankar's Medical Assistant",
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

# User database
users = {
    "doctor1": "password123",
    "doctor2": "password456"
}

# Function to call the API
def call_palmyra_api(prompt):
    # Debug information
    st.session_state['api_debug'] = {}
    
    try:
        # Check if API key exists
        if "WRITER_API_KEY" in st.secrets:
            api_key = st.secrets["WRITER_API_KEY"]
            masked_key = api_key[:4] + "..." + api_key[-4:]
            st.session_state['api_debug']['api_key'] = f"Found (masked: {masked_key})"
        else:
            st.session_state['api_debug']['api_key'] = "Not found in secrets"
            return "API key not configured. Please contact the administrator."
        
        # Try NVIDIA NIM API endpoint first
        nvidia_endpoint = "https://api.nvidia.com/v1/llm/completions"
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare payload for NVIDIA NIM API
        payload = {
            "model": "writer/palmyra-med-70b-32k",
            "messages": [
                {"role": "system", "content": "You are a medical assistant using Palmyra-Med-70B-32K model. Provide detailed, technical explanations for medical professionals."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Log what we're about to do
        st.session_state['api_debug']['request_to'] = nvidia_endpoint
        st.session_state['api_debug']['payload'] = payload
        
        # Make the API request
        response = requests.post(
            nvidia_endpoint,
            headers=headers,
            json=payload,
            timeout=30  # 30 second timeout
        )
        
        # Log response info
        st.session_state['api_debug']['status_code'] = response.status_code
        st.session_state['api_debug']['response_headers'] = dict(response.headers)
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                st.session_state['api_debug']['parsed_response'] = "Success"
                return content
            except Exception as e:
                st.session_state['api_debug']['parsing_error'] = str(e)
                st.session_state['api_debug']['response_preview'] = response.text[:500]
                return f"Error parsing API response. Please try again later."
        else:
            # Try Writer API as fallback
            writer_endpoint = "https://api.writer.com/v1/completions"
            
            # Different payload format for Writer API
            writer_payload = {
                "model": "palmyra-med-70b-32k",
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            st.session_state['api_debug']['fallback_request_to'] = writer_endpoint
            
            # Try Writer API
            try:
                writer_response = requests.post(
                    writer_endpoint,
                    headers=headers,
                    json=writer_payload,
                    timeout=30
                )
                
                st.session_state['api_debug']['fallback_status_code'] = writer_response.status_code
                
                if writer_response.status_code == 200:
                    result = writer_response.json()
                    content = result.get('choices', [{}])[0].get('text', '')
                    st.session_state['api_debug']['fallback_success'] = True
                    return content
                else:
                    st.session_state['api_debug']['fallback_error'] = writer_response.text[:500]
                    return f"Error: API returned status code {response.status_code}. Please try again later."
            except Exception as e:
                st.session_state['api_debug']['fallback_exception'] = str(e)
                return f"Error connecting to API: {str(e)}. Please try again later."
    except Exception as e:
        st.session_state['api_debug']['exception'] = str(e)
        return f"An error occurred: {str(e)}. Please try again later."

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
            st.rerun()
        else:
            st.error("Invalid username or password")

# Main application
def main_app():
    st.title("Medical Chat Assistant")
    
    # Sidebar
    with st.sidebar:
        st.header("Options")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.messages = []
            st.rerun()
        
        st.header("Prescription Analysis")
        uploaded_file = st.file_uploader("Upload a prescription", type=["jpg", "jpeg", "png", "pdf"])
        
        if uploaded_file is not None:
            st.write(f"Uploaded: {uploaded_file.name}")
            # Display the file info
            file_details = {"Filename": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": f"{uploaded_file.size / 1024:.2f} KB"}
            st.write(file_details)
            
            # Show a button to analyze the prescription
            if st.button("Analyze Prescription"):
                with st.spinner("Analyzing prescription..."):
                    # Create a prompt for prescription analysis
                    prompt = f"I am a medical professional analyzing a prescription image. I need to extract the following information: medication names, dosages, frequencies, and any special instructions. I also need to identify potential drug interactions or concerning issues."
                    
                    # Get API response
                    response = call_palmyra_api(prompt)
                    
                    # Add to chat history
                    st.session_state.messages.append({"role": "user", "content": f"Analyzed prescription: {uploaded_file.name}"})
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.info(message["content"])
        else:
            st.success(message["content"])
    
    # User input
    user_input = st.text_input("Type your medical question here...")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Send"):
            if user_input:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Create a structured prompt for medical context
                prompt = f"As a medical professional, I need information about: {user_input}. Please provide a detailed, technical explanation suitable for healthcare providers."
                
                # Call the API with a loading spinner
                with st.spinner("Generating response..."):
                    response = call_palmyra_api(prompt)
                    
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    # Debug information section
    if st.checkbox("Show API debug info", False):
        st.write("### API Debug Information")
        if 'api_debug' in st.session_state:
            st.json(st.session_state['api_debug'])

# Main logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()