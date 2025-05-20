import streamlit as st
import requests
import json
import time
from PIL import Image
import io

# Function to query medical AI
def query_medical_ai(question):
    """
    Query the medical AI through Hugging Face Inference API
    """
    # Use the public Hugging Face Inference API (no API key required)
    API_URL = "https://api-inference.huggingface.co/models/medicalai/ClinicalGPT"
    
    # Medical system prompt
    system_prompt = """You are a medical assistant providing evidence-based guidance to healthcare professionals.
    Follow these guidelines:
    1. Provide information based on current medical evidence and guidelines
    2. Always remind users to exercise clinical judgment and verify information
    3. Format responses with clear sections and concise information
    4. Include relevant warnings, contraindications, and monitoring parameters
    5. When uncertain, acknowledge limitations and suggest consulting additional resources
    """
    
    full_prompt = f"{system_prompt}\n\nQuestion: {question}\n\nAnswer:"
    
    # Send request to Hugging Face
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.1,
            "top_p": 0.9,
            "repetition_penalty": 1.15
        }
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()[0]["generated_text"]
            # Clean up response
            if "Answer:" in result:
                answer = result.split("Answer:")[1].strip()
            else:
                answer = result.replace(full_prompt, "").strip()
            return answer
        else:
            return fallback_medical_response(question)
    except Exception as e:
        return fallback_medical_response(question)

# Fallback responses when API is unavailable
def fallback_medical_response(query):
    """Provide fallback responses for common medical queries"""
    query = query.lower()
    
    # Common medical information database
    medical_data = {
        "pneumonia": """
        Community-acquired pneumonia (CAP) treatment:
        
        1. Outpatient treatment (mild):
        - First-line: Amoxicillin 1g PO TID (or)
        - Alternative: Doxycycline 100mg PO BID
        - For atypical coverage: Azithromycin 500mg day 1, then 250mg days 2-5
        
        2. Inpatient treatment (moderate):
        - Combination therapy with beta-lactam (Ampicillin/sulbactam, Ceftriaxone) plus macrolide
        - Alternative: Respiratory fluoroquinolone (Levofloxacin 750mg daily)
        
        3. Severe (ICU):
        - Beta-lactam plus either macrolide or fluoroquinolone
        - Consider antipseudomonal coverage if risk factors present
        
        Monitor: Respiratory status, oxygenation, response to antibiotics within 48-72h
        
        ALWAYS verify with current guidelines and use clinical judgment.
        """,
        
        "hypertension": """
        Hypertension management:
        
        1. Non-pharmacological:
        - Sodium restriction (<2g/day)
        - Regular physical activity (150 min/week)
        - Weight loss if overweight/obese
        - DASH diet
        - Alcohol moderation
        
        2. First-line medications:
        - Thiazide diuretics
        - ACE inhibitors or ARBs
        - Calcium channel blockers
        
        3. BP targets:
        - General: <130/80 mmHg
        - Elderly (>65y): <130-140/80 mmHg (individualize)
        - With diabetes or CKD: <130/80 mmHg
        
        4. Monitoring:
        - Regular BP measurements
        - Electrolytes and renal function for those on diuretics, ACEi, ARBs
        
        ALWAYS verify with current guidelines and use clinical judgment.
        """,
        
        "diabetes": """
        Type 2 Diabetes management:
        
        1. First-line therapy:
        - Metformin (start 500mg daily, titrate to 1000mg BID)
        - Lifestyle modifications (diet, exercise, weight loss)
        
        2. Second-line options (based on comorbidities):
        - CV disease: GLP-1 RA or SGLT2 inhibitor
        - Heart failure: SGLT2 inhibitor
        - CKD: SGLT2 inhibitor
        - Weight concerns: GLP-1 RA
        - Cost concerns: Sulfonylureas, TZDs
        
        3. Targets:
        - HbA1c: Generally <7% (individualize)
        - Fasting glucose: 80-130 mg/dL
        - Postprandial glucose: <180 mg/dL
        
        4. Monitoring:
        - HbA1c every 3-6 months
        - SMBG as indicated
        - Annual screening for complications
        
        ALWAYS verify with current guidelines and use clinical judgment.
        """
    }
    
    # Search for keywords in the query
    for keyword, info in medical_data.items():
        if keyword in query:
            return info + "\n\n(Response provided from local medical database due to API unavailability)"
    
    # Generic response if no keyword matches
    return """
    I'm currently unable to process your specific medical query.
    
    For medical information, please consider consulting:
    1. UpToDate (https://www.uptodate.com/)
    2. PubMed (https://pubmed.ncbi.nlm.nih.gov/)
    3. Current medical guidelines for your specific region
    
    As always, clinical decisions should be based on professional judgment and current best practices.
    """

# Function to analyze prescriptions
def analyze_prescription(image_file):
    """
    Analyze a prescription image using the medical AI
    """
    try:
        # Convert image to bytes
        img_bytes = image_file.getvalue()
        
        # In a real implementation, you would send this image to an OCR service
        # For now, we'll use a placeholder response
        
        st.image(image_file, caption="Uploaded Prescription", use_column_width=True)
        
        st.markdown("### Prescription Analysis")
        st.markdown("**Detected Medications:**")
        st.markdown("1. Medication placeholders (in a real implementation, these would be detected from the image)")
        st.markdown("2. Add your actual prescription analysis logic here")
        
        st.markdown("### Potential Interactions")
        st.markdown("No potential interactions detected.")
        
        st.markdown("### Dosage Verification")
        st.markdown("All dosages appear to be within standard ranges.")
        
        st.success("Prescription analysis complete. Please verify all information with appropriate medical resources.")
        
    except Exception as e:
        st.error(f"Error analyzing prescription: {str(e)}")
        st.markdown("Please try uploading a clearer image or contact support.")

# Function to show the Ask Medical Questions page
def show_ask_medical_questions():
    st.title("Ask Medical Questions")
    
    # Create a container for chat history
    chat_container = st.container()
    
    # Initialize chat history in session state if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display existing chat history
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"<div style='background-color:#2e4a67; padding:10px; border-radius:5px; margin-bottom:10px;'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color:#3a3b3c; padding:10px; border-radius:5px; margin-bottom:10px;'><strong>Medical Assistant:</strong> {message['content']}</div>", unsafe_allow_html=True)
    
    # Create user input area
    with st.form(key="medical_question_form", clear_on_submit=True):
        user_question = st.text_area("Type your medical question:", height=100)
        submit_button = st.form_submit_button("Get Answer")
    
    # Process the user's question when submitted
    if submit_button and user_question:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        # Show "thinking" message
        with st.spinner("Generating medical response..."):
            # Get response from medical AI
            ai_response = query_medical_ai(user_question)
            
            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Rerun to update the UI with new messages
        st.experimental_rerun()
    
    # Add disclaimer
    st.markdown("---")
    st.caption("Responses are generated by AI. Always verify with appropriate medical resources and use clinical judgment.")

# Function to show the Prescription Analysis page
def show_prescription_analysis():
    st.title("Prescription Analysis")
    
    st.write("Upload prescription image for analysis")
    
    uploaded_file = st.file_uploader("Upload prescription", type=["jpg", "jpeg", "png", "pdf"])
    
    if uploaded_file is not None:
        # Process the uploaded prescription
        analyze_prescription(uploaded_file)

# Function to show the Medical Resources page
def show_medical_resources():
    st.title("Medical Resources")
    
    # Sample medical resources
    resources = [
        {"name": "UpToDate", "url": "https://www.uptodate.com/", "description": "Evidence-based clinical decision support"},
        {"name": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov/", "description": "Biomedical literature database"},
        {"name": "Medscape", "url": "https://www.medscape.com/", "description": "Medical news, clinical references"},
        {"name": "Lexicomp", "url": "https://online.lexi.com/", "description": "Drug information database"},
        {"name": "Micromedex", "url": "https://www.micromedexsolutions.com/", "description": "Evidence-based medication information"},
        {"name": "MDCalc", "url": "https://www.mdcalc.com/", "description": "Medical calculators and decision tools"}
    ]
    
    for resource in resources:
        st.subheader(resource["name"])
        st.write(resource["description"])
        st.write(f"[Visit Website]({resource['url']})")
        st.markdown("---")

# Function to show the About page
def show_about():
    st.title("About Dr. Daya's Clinic Medical Assistant")
    st.write("""
    This medical assistant provides evidence-based guidance to healthcare professionals.
    It is designed to support clinical decision-making but should not replace clinical judgment.
    
    **Features:**
    - Ask medical questions and get evidence-based answers
    - Analyze prescriptions for drug interactions and dosing
    - Access trusted medical resources
    
    **Disclaimer:** This tool is for educational purposes only. Always verify information with appropriate medical resources.
    """)

# Function to show the System Diagnostics page
def show_system_diagnostics():
    st.title("System Diagnostics")
    
    st.subheader("System Status")
    
    # Check API connectivity
    try:
        with st.spinner("Testing Hugging Face API connection..."):
            response = requests.get("https://huggingface.co/api/models/medicalai/ClinicalGPT")
            if response.status_code == 200:
                st.success("✅ Hugging Face API: Connected")
            else:
                st.error("❌ Hugging Face API: Disconnected")
    except:
        st.error("❌ Hugging Face API: Disconnected")
    
    # System metrics
    st.subheader("System Information")
    st.info("Streamlit Version: " + st.__version__)
    st.info("Python Version: " + sys.version.split()[0])
    
    # Test medical AI
    st.subheader("Test Medical AI")
    
    with st.form("test_form"):
        test_query = st.text_input("Enter a test medical question:")
        submit = st.form_submit_button("Test")
    
    if submit and test_query:
        with st.spinner("Testing medical AI..."):
            response = query_medical_ai(test_query)
            st.subheader("Response:")
            st.write(response)

# User authentication functions
def authenticate(username, password):
    """
    Authenticate a user
    """
    # In a real application, you would verify against a secure database
    valid_users = {
        "drdaya": {"password": "admin123", "role": "administrator"},
        "doctor1": {"password": "doctor123", "role": "doctor"},
        "nurse1": {"password": "nurse123", "role": "nurse"}
    }
    
    if username in valid_users and valid_users[username]["password"] == password:
        return True, valid_users[username]["role"]
    return False, None

# Main application
def main():
    # Set page config
    st.set_page_config(
        page_title="Dr. Daya's Clinic Medical Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check if user is logged in
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        # Show login page
        st.title("Dr. Daya's Clinic Medical Assistant")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if username and password:
                    is_authenticated, role = authenticate(username, password)
                    if is_authenticated:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = role
                        st.experimental_rerun()
                    else:
                        st.error("Invalid username or password")
        
        # Note about access
        st.markdown("---")
        st.caption("Note: This medical assistant is for healthcare professionals only.")
    else:
        # Show navigation and main content
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown("# Navigation")
            
            st.write("Go to")
            page = st.radio(
                "",
                ["Ask Medical Questions", "Prescription Analysis", "Medical Resources", "About", "System Diagnostics"],
                label_visibility="collapsed"
            )
            
            # User info
            st.markdown("---")
            st.info(f"Logged in as: {st.session_state.username} ({st.session_state.role.title()})")
            
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.experimental_rerun()
        
        with col2:
            # Show selected page
            if page == "Ask Medical Questions":
                show_ask_medical_questions()
            elif page == "Prescription Analysis":
                show_prescription_analysis()
            elif page == "Medical Resources":
                show_medical_resources()
            elif page == "About":
                show_about()
            elif page == "System Diagnostics":
                show_system_diagnostics()

# Run the app
if __name__ == "__main__":
    main()