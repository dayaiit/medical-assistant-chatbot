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
        # Use Meditron-7B model instead
        api_url = "https://api-inference.huggingface.co/models/epfl-llm/meditron-7b"
        
        # Get API key from Streamlit secrets
        api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Simple payload for Meditron
        payload = {
            "inputs": f"You are a medical assistant for Dr. Daya's Clinic. Answer this medical question professionally: {question}",
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7
            }
        }
        
        # Call API
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        # Store debug info
        if hasattr(st.session_state, 'debug_info'):
            st.session_state.debug_info = {
                'status_code': response.status_code,
                'response_text': response.text[:100] if response.text else None
            }
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract text
            if isinstance(result, list) and len(result) > 0:
                answer = result[0].get("generated_text", "").strip()
            elif isinstance(result, dict) and "generated_text" in result:
                answer = result["generated_text"].strip()
            else:
                return get_offline_response(question)
            
            return answer
            
        elif response.status_code == 503:
            # Model is loading
            return "The AI model is currently loading. Please try again in a few moments."
        else:
            # Other error
            if hasattr(st, 'error'):
                st.error(f"API Error: {response.status_code} - {response.text}")
            return get_offline_response(question)
            
    except Exception as e:
        if hasattr(st, 'error'):
            st.error(f"Error: {str(e)}")
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
    st.write("API Key exists:", bool(st.secrets.get("HUGGINGFACE_API_KEY", "")))
    
    # Select model to test
    model_options = {
        "Meditron-7B (Medical)": "epfl-llm/meditron-7b",
        "Llama3-OpenBioLLM-8B": "aaditya/Llama3-OpenBioLLM-8B",
        "GPT-2 (Basic test)": "gpt2",
        "Mistral-7B-Instruct": "mistralai/Mistral-7B-Instruct-v0.1"
    }
    
    selected_model_name = st.selectbox("Select model to test:", list(model_options.keys()))
    selected_model = model_options[selected_model_name]
    
    if st.button("Test API Connection"):
        with st.spinner(f"Testing connection to {selected_model}..."):
            try:
                api_url = f"https://api-inference.huggingface.co/models/{selected_model}"
                api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
                headers = {"Authorization": f"Bearer {api_key}"}
                
                # Simpler test for more reliable results
                payload = {"inputs": "What is diabetes?"}
                
                st.info(f"Connecting to: {api_url}")
                response = requests.post(api_url, headers=headers, json=payload)
                
                st.write("Status Code:", response.status_code)
                if response.status_code == 200:
                    st.success("API connection successful!")
                    st.write("Response preview:")
                    result = response.json()
                    if isinstance(result, list):
                        st.write(result[0]["generated_text"][:200] + "...")
                    else:
                        st.write(str(result)[:200] + "...")
                elif response.status_code == 503:
                    st.warning("Model is loading. Try again in a few moments.")
                    st.write(response.text)
                else:
                    st.error(f"API error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
    
    st.subheader("Troubleshooting Tips")
    st.markdown("""
    - If you're seeing **404 errors**, the model might not be accessible via the Inference API
    - If you're seeing **401 errors**, your API key might be invalid or expired
    - If you're seeing **503 errors**, the model is loading - wait and try again
    - Try the "GPT-2" option as a basic test - if it works, your API key is valid
    """)

# Main logic
if not st.session_state.logged_in:
    show_login()
else:
    show_app()