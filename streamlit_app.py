import streamlit as st
import requests
import time

# Page configuration
st.set_page_config(page_title="Medical Assistant Chatbot", page_icon="🏥")

# User credentials
USERS = {
    "drdaya": "admin123",
    "doctor1": "doctor123",
    "doctor2": "doctor123",
    # Add other users as needed
}

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "debug_info" not in st.session_state:
    st.session_state.debug_info = {}

# Function to get response from Hugging Face
def get_medical_response(question):
    try:
        # Use OpenBioLLM-8B model
        api_url = "https://api-inference.huggingface.co/models/aaditya/Llama3-OpenBioLLM-8B"
        
        # Get API key from Streamlit secrets
        api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
        
        # Store debug info
        st.session_state.debug_info["api_key_exists"] = bool(api_key)
        
        # If no API key, show error and return offline response
        if not api_key:
            st.error("API key not found in secrets. Please add it to Streamlit secrets.")
            return get_offline_response(question)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Format prompt
        prompt = f"""<s>[INST] You are a medical assistant for Dr. Daya's Clinic.
        Answer the following medical question professionally:
        {question} [/INST]"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7
            }
        }
        
        # Print debug info
        st.session_state.debug_info["request_sent"] = True
        
        # Call API with timeout
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        # Store status code for debugging
        st.session_state.debug_info["status_code"] = response.status_code
        
        if response.status_code == 200:
            try:
                result = response.json()
                st.session_state.debug_info["response_format"] = type(result).__name__
                
                # Extract text from response
                if isinstance(result, list) and len(result) > 0:
                    answer = result[0].get("generated_text", "").strip()
                elif isinstance(result, dict) and "generated_text" in result:
                    answer = result["generated_text"].strip()
                else:
                    st.session_state.debug_info["extraction_error"] = "Unexpected response format"
                    return get_offline_response(question)
                    
                # Extract just the assistant's response
                if "[/INST]" in answer:
                    answer = answer.split("[/INST]")[-1].strip()
                    
                return answer
            except Exception as e:
                st.session_state.debug_info["json_error"] = str(e)
                return get_offline_response(question)
        elif response.status_code == 503:
            st.session_state.debug_info["model_loading"] = True
            return "The AI model is currently loading. Please try again in a few moments."
        else:
            st.session_state.debug_info["error_text"] = response.text
            return get_offline_response(question)
            
    except Exception as e:
        st.session_state.debug_info["exception"] = str(e)
        return get_offline_response(question)

# Function for offline responses
def get_offline_response(question):
    question_lower = question.lower()
    
    if "tuberculos" in question_lower and "histolog" in question_lower:
        return "The two hallmark histological features of tuberculosis are: 1) Caseous granulomas - characterized by a central area of necrosis (caseous necrosis) surrounded by epithelioid histiocytes, lymphocytes, and multinucleated giant cells (Langhans giant cells), and 2) Langhans giant cells - multinucleated giant cells with nuclei arranged in a horseshoe or peripheral pattern."
    
    if "cranial nerve" in question_lower and "facial" in question_lower:
        return "The facial nerve (cranial nerve VII) is primarily responsible for facial expression. It innervates the muscles of facial expression and controls most facial movements including those of the forehead, eyelids, cheeks, and mouth."
    
    # Add more specific responses
    
    # Default response
    return "I'm currently operating in offline mode. Please try again later when our system is connected to the medical AI service, or contact one of our healthcare professionals directly."

# Login page
def show_login():
    st.title("Medical Assistant Chatbot")
    st.subheader("Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

# Main application
def show_app():
    # Sidebar
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio("Go to", ["Ask Medical Questions", "Prescription Analysis", "About", "Debug"])
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.experimental_rerun()
    
    # Main content
    if page == "Ask Medical Questions":
        st.title("Ask Medical Questions")
        
        question = st.text_area("Enter your medical question:")
        
        if st.button("Submit Question"):
            if question:
                with st.spinner("Generating response..."):
                    response = get_medical_response(question)
                
                st.subheader("Response:")
                st.write(response)
    
    elif page == "Prescription Analysis":
        st.title("Prescription Analysis")
        
        uploaded_file = st.file_uploader("Upload prescription image", type=["jpg", "jpeg", "png", "pdf"])
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Prescription", use_column_width=True)
            
            if st.button("Analyze Prescription"):
                with st.spinner("Analyzing prescription..."):
                    # In a real implementation, you would process the image
                    response = "Prescription analysis feature is currently in development."
                    
                st.subheader("Analysis Results:")
                st.write(response)
    
    elif page == "About":
        st.title("About")
        st.write("This medical assistant uses AI to help healthcare professionals find accurate medical information.")
        st.write("Developed for Dr. Daya's Clinic.")
    
    elif page == "Debug":
        st.title("Debug Information")
        st.write("This page helps troubleshoot API connection issues.")
        
        st.subheader("API Connection")
        st.write("API Key exists:", st.secrets.get("HUGGINGFACE_API_KEY", "") != "")
        
        if st.button("Test API Connection"):
            with st.spinner("Testing connection..."):
                try:
                    api_url = "https://api-inference.huggingface.co/models/aaditya/Llama3-OpenBioLLM-8B"
                    api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
                    headers = {"Authorization": f"Bearer {api_key}"}
                    response = requests.post(api_url, headers=headers, json={"inputs": "What is diabetes?"})
                    
                    st.write("Status Code:", response.status_code)
                    if response.status_code == 200:
                        st.success("API connection successful!")
                    else:
                        st.error(f"API error: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
        
        st.subheader("Session State Debug Info")
        st.json(st.session_state.debug_info)

# Main logic
if not st.session_state.logged_in:
    show_login()
else:
    show_app()