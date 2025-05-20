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

# Function to get response from Hugging Face
def get_medical_response(question):
    try:
        # Use OpenBioLLM-8B model
        api_url = "https://api-inference.huggingface.co/models/aaditya/Llama3-OpenBioLLM-8B"
        
        # Get API key from Streamlit secrets
        api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
        
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
        
        # Call API
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Store status code for debugging
        st.session_state.last_status_code = response.status_code
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract text from response
            if isinstance(result, list) and len(result) > 0:
                answer = result[0].get("generated_text", "").strip()
            elif isinstance(result, dict) and "generated_text" in result:
                answer = result["generated_text"].strip()
            else:
                return get_offline_response(question)
                
            # Extract just the assistant's response
            if "[/INST]" in answer:
                answer = answer.split("[/INST]")[-1].strip()
                
            return answer
        else:
            # Fall back to offline response
            return get_offline_response(question)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return get_offline_response(question)

# Function for offline responses
def get_offline_response(question):
    question_lower = question.lower()
    
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
    
    page = st.sidebar.radio("Go to", ["Ask Medical Questions", "Prescription Analysis", "About"])
    
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
        
        # Debug section (remove in production)
        if st.checkbox("Show Debug Info"):
            st.write("API Key exists:", bool(st.secrets.get("HUGGINGFACE_API_KEY", "")))
            if "last_status_code" in st.session_state:
                st.write("Last API Status Code:", st.session_state.last_status_code)

# Main logic
if not st.session_state.logged_in:
    show_login()
else:
    show_app()