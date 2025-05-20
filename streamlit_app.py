import streamlit as st
import requests
import json
import time

# Set page title and configuration
st.set_page_config(
    page_title="Dr. Daya's Clinic Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

# Define user credentials (in a real app, use a more secure method)
USERS = {
    "drdaya": "admin123",
    "doctor1": "doctor123",
    "doctor2": "doctor123",
    "nurse1": "nurse123",
    "nurse2": "nurse123",
    "nurse3": "nurse123",
    "nurse4": "nurse123",
    "nurse5": "nurse123",
    "pharmacy": "pharm123",
    "manager": "manager123"
}

# Function to call Hugging Face's Inference API
def query_medical_llm(prompt, model_name="aaditya/Llama3-OpenBioLLM-8B"):
    api_url = f"https://api-inference.huggingface.co/models/{model_name}"
    
    # Get API key from Streamlit secrets (add your key in Streamlit Cloud secrets)
    api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Format the prompt properly for LLM models
    formatted_prompt = f"""
    <s>[INST] You are an AI medical assistant for Dr. Daya's Clinic. Answer the following medical query professionally:
    {prompt} [/INST]
    """
    
    data = {
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        
        # Check if model is still loading
        if response.status_code == 503:
            return "Model is loading. Please try again in a few moments."
        
        result = response.json()
        
        # Handle different response formats
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").split("[/INST]")[-1].strip()
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"].split("[/INST]")[-1].strip()
        else:
            # Fallback response
            return "I couldn't generate a response. Please try again."
            
    except Exception as e:
        # If API call fails, use the fallback response system
        return get_fallback_response(prompt)

# Fallback response function for when API is unavailable
def get_fallback_response(prompt):
    # Basic keyword matching for common medical queries
    prompt_lower = prompt.lower()
    
    if "headache" in prompt_lower:
        return "Headaches can be caused by various factors including stress, dehydration, lack of sleep, or underlying medical conditions. For occasional headaches, over-the-counter pain relievers may help. If headaches are severe or persistent, please consult with your doctor."
    
    elif "blood pressure" in prompt_lower:
        return "Normal blood pressure is typically around 120/80 mmHg. Hypertension (high blood pressure) is generally considered to be 130/80 mmHg or higher. Regular monitoring and lifestyle modifications such as healthy diet, regular exercise, and stress management are important for maintaining healthy blood pressure."
    
    elif "diabetes" in prompt_lower:
        return "Diabetes is a chronic condition characterized by high blood sugar levels. Common symptoms include increased thirst, frequent urination, unexplained weight loss, fatigue, and blurred vision. Management typically involves monitoring blood glucose levels, medication or insulin therapy, healthy eating, and regular physical activity."
    
    # Add more fallback responses for common queries
    
    else:
        return "I'm currently operating in offline mode. Please try again later when our system is connected to the medical AI service, or contact one of our healthcare professionals directly."

# Login interface
def login_page():
    st.title("Dr. Daya's Clinic Medical Assistant")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")

# Main application
def main_app():
    st.title(f"Dr. Daya's Clinic Medical Assistant")
    st.subheader(f"Welcome, {st.session_state.username}")
    
    # Sidebar for navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Ask Medical Questions", "Prescription Analysis", "About"])
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    # Ask Medical Questions page
    if page == "Ask Medical Questions":
        st.header("Ask Medical Questions")
        
        user_question = st.text_area("Enter your medical question:", height=150)
        
        if st.button("Submit Question"):
            if user_question:
                with st.spinner("Generating response..."):
                    # Add artificial delay to simulate processing
                    time.sleep(1)
                    response = query_medical_llm(user_question)
                    
                st.subheader("Response:")
                st.write(response)
            else:
                st.warning("Please enter a question.")
    
    # Prescription Analysis page
    elif page == "Prescription Analysis":
        st.header("Prescription Analysis")
        
        uploaded_file = st.file_uploader("Upload prescription image", type=["jpg", "jpeg", "png", "pdf"])
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Prescription", use_column_width=True)
            
            if st.button("Analyze Prescription"):
                with st.spinner("Analyzing prescription..."):
                    # Simulate processing time
                    time.sleep(2)
                    
                    # In a real implementation, you would extract text from the image and send to LLM
                    prompt = "Analyze this prescription and provide a summary of medications, dosages, and potential interactions."
                    response = query_medical_llm(prompt)
                    
                st.subheader("Analysis Results:")
                st.write(response)
    
    # About page
    elif page == "About":
        st.header("About Dr. Daya's Medical Assistant")
        st.write("""
        This Medical Assistant uses advanced AI to provide reliable medical information to healthcare professionals at Dr. Daya's Clinic.
        
        **Features:**
        - Medical question answering
        - Prescription analysis
        - Evidence-based information
        
        **Note:** This assistant is designed as a support tool for healthcare professionals and should not replace professional medical judgment.
        
        **Version:** 1.0
        """)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()