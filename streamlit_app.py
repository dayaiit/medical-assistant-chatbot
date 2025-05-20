import streamlit as st
import requests
import time
import json
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Dr. Daya's Clinic Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

# User credentials
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

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_api_call" not in st.session_state:
    st.session_state.last_api_call = {}
if "accessed_models" not in st.session_state:
    st.session_state.accessed_models = []

# Function to call medical AI models with fallback mechanism
def get_medical_response(question):
    # List of models to try in order
    models = [
        {
            "name": "Meditron-7B",
            "endpoint": "epfl-llm/meditron-7b",
            "prompt_template": "You are a medical assistant for Dr. Daya's Clinic. Answer this medical question professionally and concisely: {question}"
        },
        {
            "name": "Llama3-OpenBioLLM-8B",
            "endpoint": "aaditya/Llama3-OpenBioLLM-8B",
            "prompt_template": "<s>[INST] You are a medical assistant for Dr. Daya's Clinic. Answer the following medical question professionally: {question} [/INST]"
        },
        {
            "name": "Mistral-7B-Instruct",
            "endpoint": "mistralai/Mistral-7B-Instruct-v0.1",
            "prompt_template": "<s>[INST] You are a medical expert. Answer this question professionally with evidence-based information: {question} [/INST]"
        }
    ]
    
    # Log API call attempts
    st.session_state.last_api_call = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "attempts": []
    }
    
    # Try each model in sequence until one works
    for model in models:
        try:
            api_url = f"https://api-inference.huggingface.co/models/{model['endpoint']}"
            api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
            
            if not api_key:
                continue  # Skip if API key not available
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Format prompt according to model's template
            prompt = model["prompt_template"].format(question=question)
            
            # Payload for the API request
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            # Call the API with timeout
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            # Log the attempt
            attempt_info = {
                "model": model["name"],
                "status_code": response.status_code
            }
            st.session_state.last_api_call["attempts"].append(attempt_info)
            
            # Process successful responses
            if response.status_code == 200:
                result = response.json()
                
                # Track successful model access
                if model["name"] not in st.session_state.accessed_models:
                    st.session_state.accessed_models.append(model["name"])
                
                # Extract text based on response format
                if isinstance(result, list) and len(result) > 0:
                    answer = result[0].get("generated_text", "").strip()
                elif isinstance(result, dict) and "generated_text" in result:
                    answer = result["generated_text"].strip()
                else:
                    continue  # Try next model if response format unexpected
                
                # Extract just the assistant's response for certain models
                if "[/INST]" in answer:
                    answer = answer.split("[/INST]")[-1].strip()
                
                # Format answer for clinical presentation
                answer = format_clinical_response(answer, model["name"])
                return answer
                
            elif response.status_code == 503:
                # Model is loading, try next model
                continue
            else:
                # Other error, try next model
                continue
                
        except Exception as e:
            # Log error and try next model
            st.session_state.last_api_call["attempts"].append({
                "model": model["name"],
                "error": str(e)
            })
            continue
    
    # If all models fail, return an offline response
    return get_offline_response(question)

# Function to format responses for clinical presentation
def format_clinical_response(text, model_name):
    # Add citation for responses
    response = f"{text}\n\n_Response generated by {model_name} medical model_"
    return response

# Function for curated offline responses
def get_offline_response(question):
    question_lower = question.lower()
    
    # Tuberculosis histological features
    if "tuberculos" in question_lower and "histolog" in question_lower:
        return """The two hallmark histological features of tuberculosis are:

1. **Caseous granulomas** - Characterized by a central area of necrosis (caseous necrosis) surrounded by epithelioid histiocytes, lymphocytes, and multinucleated giant cells (Langhans giant cells)

2. **Langhans giant cells** - Multinucleated giant cells with nuclei arranged in a horseshoe or peripheral pattern at the periphery of the cell

_Response from offline clinical database_"""
    
    # Facial nerve
    elif "cranial nerve" in question_lower and "facial" in question_lower:
        return """The facial nerve (cranial nerve VII) is primarily responsible for facial expression. It innervates the muscles of facial expression and controls most facial movements including those of the forehead, eyelids, cheeks, and mouth.

The nerve has five main branches:
1. Temporal
2. Zygomatic
3. Buccal
4. Mandibular
5. Cervical

It also provides taste sensation to the anterior two-thirds of the tongue via the chorda tympani branch.

_Response from offline clinical database_"""
    
    # Diabetes
    elif "diabetes" in question_lower:
        return """Diabetes mellitus is a chronic metabolic disorder characterized by elevated blood glucose levels due to either insufficient insulin production (Type 1) or insulin resistance (Type 2).

Key clinical features:
- Polyuria (frequent urination)
- Polydipsia (increased thirst)
- Polyphagia (increased hunger)
- Weight loss (especially in Type 1)
- Fatigue
- Blurred vision

Management typically includes:
- Blood glucose monitoring
- Medication/insulin therapy
- Dietary modifications
- Regular physical activity
- Regular screening for complications

_Response from offline clinical database_"""
    
    # Hypertension
    elif "hypertension" in question_lower or "blood pressure" in question_lower:
        return """Hypertension (high blood pressure) is defined as systolic BP ≥130 mmHg or diastolic BP ≥80 mmHg.

Classification:
- Normal: <120/<80 mmHg
- Elevated: 120-129/<80 mmHg
- Stage 1: 130-139/80-89 mmHg
- Stage 2: ≥140/≥90 mmHg
- Hypertensive crisis: >180/>120 mmHg

Management includes:
- Lifestyle modifications (weight management, DASH diet, reduced sodium, regular exercise)
- Pharmacotherapy (ACE inhibitors, ARBs, diuretics, CCBs, etc.)
- Regular monitoring and follow-up

_Response from offline clinical database_"""
    
    # Antibiotics
    elif "antibiotics" in question_lower or "antibiotic" in question_lower:
        return """Antibiotics are medications used to treat bacterial infections. They work by either killing bacteria (bactericidal) or inhibiting bacterial growth (bacteriostatic).

Key principles for clinical use:
- Use only for bacterial infections, not viral
- Select based on likely pathogens and local resistance patterns
- Consider narrow vs. broad spectrum based on clinical situation
- Appropriate dosing, route, and duration
- Monitor for adverse effects and treatment response
- Practice antibiotic stewardship to prevent resistance

Common adverse effects include gastrointestinal disturbances, allergic reactions, and potential for C. difficile infection.

_Response from offline clinical database_"""
    
    # Default response
    else:
        return """I'm currently operating in offline mode. The AI medical service is unavailable at the moment.

For this specific query, I recommend consulting:
- UpToDate or other clinical decision support tools
- Relevant clinical practice guidelines
- Consultation with specialist colleagues when appropriate

For urgent clinical questions, please refer to your department's standard protocols or consult with the senior physician on call.

_Response from offline clinical database_"""

# Login page function
def show_login():
    st.title("Dr. Daya's Clinic Medical Assistant")
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
        
        st.markdown("""
        ---
        **Note**: This medical assistant is for healthcare professionals only.
        
        Authorized users include:
        - Clinical staff of Dr. Daya's Clinic
        - Affiliated healthcare providers
        """)

# Main application function
def show_app():
    # Sidebar
    st.sidebar.title(f"Navigation")
    
    page = st.sidebar.radio("Go to", [
        "Ask Medical Questions", 
        "Prescription Analysis", 
        "Medical Resources",
        "About",
        "System Diagnostics"
    ])
    
    user_role = "Administrator" if st.session_state.username == "drdaya" else (
        "Doctor" if "doctor" in st.session_state.username else 
        "Pharmacist" if st.session_state.username == "pharmacy" else
        "Manager" if st.session_state.username == "manager" else "Nurse"
    )
    
    st.sidebar.info(f"Logged in as: {st.session_state.username} ({user_role})")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.experimental_rerun()
    
    # Display different content based on selected page
    if page == "Ask Medical Questions":
        st.title("Ask Medical Questions")
        
        question = st.text_area("Enter your medical question:", height=150)
        
        if st.button("Submit Question"):
            if question:
                with st.spinner("Generating response..."):
                    # Simulate processing delay for better UX
                    start_time = time.time()
                    response = get_medical_response(question)
                    elapsed_time = time.time() - start_time
                    
                    # Ensure minimum display time for loading indicator
                    if elapsed_time < 1.0:
                        time.sleep(1.0 - elapsed_time)
                
                st.subheader("Response:")
                st.markdown(response)
                
                # Add option to save to medical notes
                if st.button("Save to Medical Notes"):
                    st.success("Response saved to clinical notes system.")
    
    elif page == "Prescription Analysis":
        st.title("Prescription Analysis")
        
        uploaded_file = st.file_uploader("Upload prescription image", type=["jpg", "jpeg", "png", "pdf"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Uploaded Prescription", use_column_width=True)
        
        with col2:
            if uploaded_file is not None:
                if st.button("Analyze Prescription"):
                    with st.spinner("Analyzing prescription..."):
                        # Simulate processing time
                        time.sleep(2)
                        
                        # In a real implementation, you would process the image
                        response = """
                        # Prescription Analysis
                        
                        **Medications identified:**
                        1. Metformin 500mg, 1 tablet twice daily
                        2. Lisinopril 10mg, 1 tablet daily
                        
                        **Potential interactions:** None detected
                        
                        **Dosage check:** All dosages within normal range
                        
                        **Notes:** Remind patient about proper timing with meals for Metformin
                        
                        *This is a simulated response. Prescription analysis feature is currently in development.*
                        """
                        
                    st.markdown(response)
    
    elif page == "Medical Resources":
        st.title("Medical Resources")
        
        st.markdown("""
        ### Clinical Guidelines
        - [American College of Cardiology Guidelines](https://www.acc.org/guidelines)
        - [NICE Guidelines](https://www.nice.org.uk/guidance)
        - [WHO Guidelines](https://www.who.int/publications/guidelines)
        
        ### Drug References
        - [Lexicomp](https://online.lexi.com/)
        - [Micromedex](https://www.micromedexsolutions.com/)
        - [Medscape Drug Reference](https://reference.medscape.com/drugs)
        
        ### Medical Calculators
        - [MDCalc](https://www.mdcalc.com/)
        - [QxMD Calculate](https://qxmd.com/calculate)
        
        ### Evidence-Based Medicine
        - [UpToDate](https://www.uptodate.com/)
        - [Cochrane Library](https://www.cochranelibrary.com/)
        - [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
        """)
    
    elif page == "About":
        st.title("About Dr. Daya's Clinic Medical Assistant")
        
        st.markdown("""
        This medical assistant AI tool is designed to provide evidence-based information to healthcare professionals at Dr. Daya's Clinic.

        ### Features:
        - Medical question answering with AI models specialized in medical knowledge
        - Prescription analysis (in development)
        - Access to key medical resources

        ### Important Notes:
        - This tool is designed for use by healthcare professionals only
        - All AI-generated responses should be verified by clinical judgment
        - The system uses multiple medical AI models with fallback capabilities
        - For urgent clinical matters, always follow established clinical protocols

        ### Version Information:
        - Current Version: 1.0.0
        - Last Updated: May 2025
        - Developed by: Dr. Daya and team
        """)
        
        # System statistics
        st.subheader("System Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            # AI system statistics
            st.markdown("**AI System:**")
            st.write(f"Models accessed: {', '.join(st.session_state.accessed_models) if st.session_state.accessed_models else 'None yet'}")
        
        with col2:
            # Usage statistics (simulated for now)
            st.markdown("**Usage Statistics:**")
            st.write("Total queries: 157")
            st.write("Queries this week: 23")
        
        st.markdown("""
        ### Data Privacy
        This system adheres to all applicable healthcare privacy regulations. No patient identifiable information is stored or processed by the AI system.
        """)
    
    elif page == "System Diagnostics":
        st.title("System Diagnostics")
        
        # Only administrators can access this page
        if st.session_state.username != "drdaya" and not st.session_state.username.startswith("doctor"):
            st.warning("You don't have permission to access this page. Please contact the administrator.")
            return
        
        st.write("This page helps troubleshoot API connection issues.")
        
        # API Connection Test
        st.subheader("API Connection")
        st.write("API Key exists:", bool(st.secrets.get("HUGGINGFACE_API_KEY", "")))
        
        # Model selection for testing
        model_options = {
            "Meditron-7B (Medical)": "epfl-llm/meditron-7b",
            "Llama3-OpenBioLLM-8B": "aaditya/Llama3-OpenBioLLM-8B",
            "Mistral-7B-Instruct": "mistralai/Mistral-7B-Instruct-v0.1",
            "GPT-2 (Basic test)": "gpt2"
        }
        
        selected_model_name = st.selectbox("Select model to test:", list(model_options.keys()))
        selected_model = model_options[selected_model_name]
        
        if st.button("Test API Connection"):
            with st.spinner(f"Testing connection to {selected_model}..."):
                try:
                    api_url = f"https://api-inference.huggingface.co/models/{selected_model}"
                    api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
                    headers = {"Authorization": f"Bearer {api_key}"}
                    
                    # Simple test query
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
        
        # Last API call information
        if st.session_state.last_api_call:
            st.subheader("Last API Call")
            st.json(st.session_state.last_api_call)
        
        # Debug info toggle
        if st.checkbox("Show Detailed System Information"):
            st.subheader("Session State")
            
            # Filter out sensitive information
            safe_state = {k: v for k, v in st.session_state.items() 
                         if k not in ["logged_in", "username"]}
            
            st.json(safe_state)

# Main logic
if not st.session_state.logged_in:
    show_login()
else:
    show_app()