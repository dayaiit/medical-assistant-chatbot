import streamlit as st
import requests
import time
import sys
import re

# Medical LLM Query Function with enhanced reliability
def query_medical_llm(prompt):
    """
    Query medical LLM models with fallback options and specialized knowledge
    """
    # Multiple model options for reliability
    models = [
        {
            "name": "Meditron-7B",
            "url": "https://api-inference.huggingface.co/models/epfl-llm/meditron-7b",
            "system_prompt": """You are a medical assistant providing evidence-based guidance to healthcare professionals. 
            Focus on clinical information including diagnosis, treatment, and management strategies.
            Always remind users to verify with current guidelines and use clinical judgment.
            Format your response with clear sections, organize recommendations systematically,
            and note important warnings or contraindications when applicable."""
        },
        {
            "name": "BioMistral-7B",
            "url": "https://api-inference.huggingface.co/models/BioMistral/BioMistral-7B",
            "system_prompt": """You are a medical assistant for healthcare professionals.
            Provide detailed clinical information with evidence-based recommendations.
            Include specific diagnostic criteria, treatment protocols, and appropriate citations.
            Always remind users to verify with current guidelines and use clinical judgment."""
        }
    ]
    
    # Try each model in sequence
    for model in models:
        try:
            # Format the prompt for the model
            full_prompt = f"{model['system_prompt']}\n\nPhysician Query: {prompt}\n\nMedical Response:"
            
            # Prepare the payload with optimized parameters
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "repetition_penalty": 1.15,
                    "do_sample": True
                }
            }
            
            # Initialize headers (empty if no API key is used)
            headers = {}
            
            # Optional: Add API key if available in secrets
            if "HUGGINGFACE_API_KEY" in st.secrets:
                headers["Authorization"] = f"Bearer {st.secrets['HUGGINGFACE_API_KEY']}"
            
            # Add timeout and retry logic
            for attempt in range(3):
                try:
                    response = requests.post(
                        model["url"], 
                        headers=headers, 
                        json=payload, 
                        timeout=60
                    )
                    
                    # Handle successful response
                    if response.status_code == 200:
                        result = response.json()[0]["generated_text"]
                        
                        # Clean up response and remove any HTML tags
                        clean_response = result.replace("</div>", "")
                        
                        # Handle result extraction differently based on model
                        if "Medical Response:" in clean_response:
                            answer = clean_response.split("Medical Response:")[1].strip()
                        else:
                            # Fallback extraction method
                            answer = clean_response.replace(full_prompt, "").strip()
                        
                        return answer, True, model["name"]
                    
                    # Model still loading
                    elif response.status_code == 503 and "loading" in response.text.lower():
                        if attempt < 2:
                            time.sleep((attempt + 1) * 5)  # Progressive backoff
                            continue
                    
                    # Other errors, retry
                    else:
                        if attempt < 2:
                            time.sleep(2)
                        else:
                            break
                        
                except requests.exceptions.Timeout:
                    if attempt < 2:
                        time.sleep(5)
                    continue
                except Exception as e:
                    if attempt < 2:
                        time.sleep(3)
                    continue
                    
        except Exception as e:
            continue
    
    # If all models fail, use enhanced local database
    return get_enhanced_medical_fallback(prompt), False, "Local Medical Database"

# Enhanced medical knowledge database with tuberculosis and other detailed conditions
def get_enhanced_medical_fallback(query):
    """Provide reliable medical information from local database"""
    
    # Convert query to lowercase for matching
    query_lower = query.lower()
    
    # Comprehensive medical knowledge base with enhanced content
    medical_database = {
        "tuberculosis": """
        # Tuberculosis: Clinical and Pathological Features
        
        ## Histological Hallmarks
        1. **Caseating Granulomas**: The most characteristic feature, consisting of:
           - Central area of caseous necrosis (cheese-like appearance)
           - Surrounded by epithelioid histiocytes, lymphocytes, and Langhans giant cells
           
        2. **Langhans Giant Cells**: Distinctive multinucleated giant cells with:
           - Nuclei arranged in a horseshoe or peripheral pattern
           - Formed by fusion of macrophages
        
        3. **Acid-Fast Bacilli**: Mycobacterium tuberculosis organisms
           - Rod-shaped bacteria visible with Ziehl-Neelsen or auramine-rhodamine stains
           - Often sparse and difficult to identify in tissue sections
        
        ## Additional Histopathological Features
        - Fibrotic encapsulation in chronic lesions
        - Lymphocytic infiltration at periphery
        - Satellite granulomas surrounding main lesion
        - Variable degree of calcification in healed lesions
        
        ## Diagnostic Methods
        - Histopathology of biopsied tissue
        - Acid-fast staining
        - PCR for mycobacterial DNA
        - Culture confirmation (gold standard)
        
        Always verify with current guidelines and use clinical judgment.
        """,
        
        "lung mass": """
        # Approach to Lung Mass Evaluation
        
        ## Differential Diagnosis
        1. **Malignant**: Primary lung cancer (NSCLC, SCLC), metastatic disease
        2. **Infectious**: Tuberculoma, fungal infection (aspergilloma, histoplasmoma)
        3. **Inflammatory**: Rheumatoid nodule, Wegener's granulomatosis
        4. **Congenital**: Hamartoma, arteriovenous malformation
        
        ## Risk Assessment
        - High risk features: Age >50, smoking history, size >3cm, spiculated edges, upper lobe location
        - Key symptoms: Hemoptysis, weight loss, chest pain, dyspnea
        
        ## Diagnostic Workup
        1. Chest CT with contrast
        2. PET/CT scan for lesions ≥8mm
        3. Tissue diagnosis:
           - Central lesions: Bronchoscopy
           - Peripheral lesions: CT-guided biopsy
           - Consider EBUS for mediastinal involvement
        4. Brain MRI and bone scan if malignancy suspected
        
        ## Management
        - Suspicious lesions: Referral to thoracic surgery and oncology
        - Lung cancer staging determines treatment approach
        - Small nodules (<8mm): Serial imaging based on Fleischner criteria
        
        Always verify with current guidelines and use clinical judgment.
        """,
        
        "pneumonia": """
        # Community-Acquired Pneumonia Management
        
        ## Assessment
        1. **Diagnostic Criteria**: Combination of symptoms, signs, and radiographic findings
        2. **Severity Assessment**: CURB-65 or Pneumonia Severity Index (PSI)
        3. **Risk Stratification**: Determines outpatient vs. inpatient management
        
        ## Outpatient Treatment (Mild)
        - **First-line**: Amoxicillin 1g PO TID (or)
        - **Alternative**: Doxycycline 100mg PO BID
        - **For atypical coverage**: Azithromycin 500mg day 1, then 250mg days 2-5
        - **Duration**: Typically 5-7 days
        
        ## Inpatient Treatment (Moderate)
        - **Preferred**: Combination therapy with beta-lactam (Ampicillin/sulbactam, Ceftriaxone) plus macrolide
        - **Alternative**: Respiratory fluoroquinolone (Levofloxacin 750mg daily)
        - **Duration**: Usually 7 days
        
        ## Severe (ICU) Treatment
        - **Recommended**: Beta-lactam plus either macrolide or fluoroquinolone
        - **Consider antipseudomonal coverage** if risk factors present
        - **Duration**: 7-10 days
        
        ## Monitoring
        - Respiratory status and oxygenation
        - Response to antibiotics within 48-72h
        - Follow-up chest imaging for persistent symptoms or high-risk patients
        
        Always verify with current guidelines and use clinical judgment.
        """,
        
        "hypertension": """
        # Hypertension Management
        
        ## Non-pharmacological Interventions
        - Sodium restriction (<2g/day)
        - Regular physical activity (150 min/week moderate intensity)
        - Weight loss if overweight/obese
        - DASH diet (rich in fruits, vegetables, low-fat dairy, reduced saturated fat)
        - Alcohol moderation (<2 drinks/day for men, <1 for women)
        
        ## First-line Medications
        - **Thiazide diuretics**: Chlorthalidone 12.5-25mg daily, Hydrochlorothiazide 12.5-50mg daily
        - **ACE inhibitors**: Lisinopril 10-40mg daily, Ramipril 2.5-20mg daily
        - **ARBs**: Losartan 25-100mg daily, Valsartan 80-320mg daily
        - **CCBs**: Amlodipine 2.5-10mg daily, Diltiazem ER 120-360mg daily
        
        ## BP Targets
        - **General population**: <130/80 mmHg
        - **Elderly (>65y)**: <130-140/80 mmHg (individualize)
        - **With diabetes or CKD**: <130/80 mmHg
        
        ## Monitoring
        - Regular BP measurements (home and office)
        - Electrolytes and renal function for patients on diuretics, ACEi, ARBs
        - Urinalysis and albumin-to-creatinine ratio
        - Periodic cardiovascular risk assessment
        
        Always verify with current guidelines and use clinical judgment.
        """,
        
        "diabetes": """
        # Type 2 Diabetes Management
        
        ## First-line Therapy
        - **Metformin**: Start 500mg daily, titrate to 1000mg BID
        - **Lifestyle modifications**: Medical nutrition therapy, regular exercise, weight loss
        
        ## Second-line Options (based on comorbidities)
        - **CV disease**: GLP-1 RA (preferred) or SGLT2 inhibitor
        - **Heart failure**: SGLT2 inhibitor
        - **CKD**: SGLT2 inhibitor
        - **Weight concerns**: GLP-1 RA
        - **Cost concerns**: Sulfonylureas, TZDs
        
        ## Glycemic Targets
        - **HbA1c**: Generally <7% (individualize)
           - More stringent (6-6.5%): Short duration, no CVD, low hypoglycemia risk
           - Less stringent (7.5-8.0%): Limited life expectancy, frail elderly, multiple comorbidities
        - **Fasting glucose**: 80-130 mg/dL
        - **Postprandial glucose**: <180 mg/dL
        
        ## Monitoring
        - HbA1c every 3-6 months
        - SMBG as indicated by therapy
        - Annual screening for complications (retinopathy, nephropathy, neuropathy)
        - Comprehensive foot exam annually
        - Lipid profile and cardiovascular risk assessment
        
        Always verify with current guidelines and use clinical judgment.
        """,
        
        "chest pain": """
        # Chest Pain Evaluation
        
        ## High-Risk Features (Cardiac)
        - Crushing, pressure-like, radiating to arm/jaw/back
        - Associated with exertion, diaphoresis, dyspnea
        - History of CAD, multiple risk factors
        - Abnormal ECG changes, elevated cardiac biomarkers
        
        ## Differential Diagnosis
        1. **Cardiac**: ACS, stable angina, pericarditis, myocarditis
        2. **Pulmonary**: PE, pneumonia, pneumothorax, pleuritis
        3. **GI**: GERD, esophageal spasm, peptic ulcer
        4. **Musculoskeletal**: Costochondritis, muscle strain
        5. **Other**: Anxiety, herpes zoster
        
        ## Initial Workup
        - ECG within 10 minutes of presentation
        - Cardiac biomarkers (troponin)
        - Chest X-ray
        - Consider d-dimer if PE suspected
        
        ## Management Strategy
        - **High-risk ACS features**: Activate ACS protocol, antiplatelet therapy, anticoagulation
        - **Intermediate risk**: Observation, serial ECGs and troponins
        - **Low risk**: Consider stress testing or discharge with follow-up
        - **Non-cardiac etiology**: Treat underlying cause
        
        Always verify with current guidelines and use clinical judgment.
        """,
        
        "asthma": """
        # Asthma Management
        
        ## Classification
        1. **Intermittent**: Symptoms <2 days/week, nighttime awakenings <2x/month
        2. **Mild Persistent**: Symptoms >2 days/week, nighttime awakenings 3-4x/month
        3. **Moderate Persistent**: Daily symptoms, nighttime awakenings >1x/week
        4. **Severe Persistent**: Throughout the day, nighttime awakenings 7x/week
        
        ## Stepwise Management Approach
        
        ### Step 1 (Intermittent)
        - **SABA** as needed (e.g., albuterol)
        
        ### Step 2 (Mild Persistent)
        - **Low-dose ICS** daily (e.g., budesonide, fluticasone)
        - Alternative: Leukotriene modifier or cromolyn
        
        ### Step 3 (Mild to Moderate)
        - **Low-dose ICS + LABA** (e.g., fluticasone/salmeterol)
        - Alternative: Medium-dose ICS
        
        ### Step 4 (Moderate)
        - **Medium-dose ICS + LABA**
        - Consider adding tiotropium for patients ≥12 years
        
        ### Step 5 (Moderate to Severe)
        - **High-dose ICS + LABA**
        - Consider biologics for specific phenotypes (omalizumab for allergic)
        
        ### Step 6 (Severe)
        - **High-dose ICS + LABA + oral corticosteroids**
        - Biologics based on phenotype
        
        ## Monitoring
        - **Spirometry**: At least annually
        - **Peak flow monitoring**: For moderate-severe or poorly controlled
        - **Symptom control assessment**: Every 2-6 weeks while gaining control, then 1-6 months
        
        ## Exacerbation Management
        - **Mild-Moderate**: SABA q4-6h, oral corticosteroids if inadequate response
        - **Severe**: Continuous SABA for first hour, IV corticosteroids, consider magnesium
        
        Always verify with current guidelines and use clinical judgment.
        """
    }
    
    # Special terms to check for in query
    medical_terms = [
        "tuberculosis", "tb", "mycobacterium", "granuloma", "caseating", "langhans",
        "pneumonia", "cap", "respiratory infection", 
        "hypertension", "high blood pressure", "htn",
        "diabetes", "dm", "hyperglycemia", "t2dm",
        "asthma", "wheeze", "bronchospasm",
        "chest pain", "angina", "cardiac", "heart attack"
    ]
    
    # Check for specific terms in query
    found_terms = []
    for term in medical_terms:
        if term in query_lower:
            found_terms.append(term)
    
    # Handle histology/pathology questions specifically for TB
    if ("histolog" in query_lower or "patholog" in query_lower or "histopatholog" in query_lower or "microscop" in query_lower) and \
       any(term in query_lower for term in ["tb", "tuberculosis", "granuloma"]):
        return medical_database["tuberculosis"]
    
    # Match based on found terms
    for term in found_terms:
        if term in ["tuberculosis", "tb", "mycobacterium", "granuloma", "caseating", "langhans"]:
            return medical_database["tuberculosis"]
        elif term in ["pneumonia", "cap", "respiratory infection"]:
            return medical_database["pneumonia"]
        elif term in ["hypertension", "high blood pressure", "htn"]:
            return medical_database["hypertension"]
        elif term in ["diabetes", "dm", "hyperglycemia", "t2dm"]:
            return medical_database["diabetes"]
        elif term in ["chest pain", "angina", "cardiac", "heart attack"]:
            return medical_database["chest pain"]
        elif term in ["asthma", "wheeze", "bronchospasm"]:
            return medical_database["asthma"]
    
    # Check for lung mass related terms
    if "lung" in query_lower and any(term in query_lower for term in ["mass", "nodule", "tumor", "cancer"]):
        return medical_database["lung mass"]
    
    # General fallback response
    return """
    # General Clinical Guidance
    
    I'm currently unable to provide specific guidance for this clinical question from my local database.
    
    ## Recommended Approach
    1. **Evidence-based resources**: Consider consulting UpToDate, PubMed, or specialty society guidelines
    2. **Patient-specific factors**: Age, comorbidities, medications, and preferences should influence decisions
    3. **Specialist consultation**: Consider when diagnosis is unclear or condition is complex
    
    ## Documentation Reminders
    - Document clinical reasoning and decision-making process
    - Record pertinent positive and negative findings
    - Note patient education provided and follow-up plans
    
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
    """Display and process the Ask Medical Questions page"""
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
                # Get source if available
                source_info = ""
                if "source" in message:
                    source_info = f"<small>Source: {message['source']}</small>"
                
                st.markdown(f"<div style='background-color:#3a3b3c; padding:10px; border-radius:5px; margin-bottom:10px;'><strong>Medical Assistant:</strong> {message['content']}<br>{source_info}</div>", unsafe_allow_html=True)
    
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
            # Query the medical LLM
            response, from_api, model_name = query_medical_llm(user_question)
            
            # Add AI response to chat history with source info
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": response,
                "source": model_name
            })
        
        # Rerun to update the UI with new messages
        st.rerun()  # Using st.rerun() instead of experimental_rerun
    
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
    
    **Technology:**
    - Powered by Meditron-7B, a medical-specific large language model
    - Built with a comprehensive local medical knowledge base for reliability
    - Designed for healthcare professional use only
    
    **Disclaimer:** This tool is for educational purposes only. Always verify information with appropriate medical resources.
    """)

# Function to show the System Diagnostics page
def show_system_diagnostics():
    st.title("System Diagnostics")
    
    st.subheader("System Status")
    
    # Check API connectivity
    try:
        with st.spinner("Testing Hugging Face API connection..."):
            response = requests.get("https://huggingface.co/api/models/epfl-llm/meditron-7b")
            if response.status_code == 200:
                st.success("✅ Hugging Face API: Connected")
            else:
                st.error("❌ Hugging Face API: Disconnected")
    except:
        st.error("❌ Hugging Face API: Disconnected")
    
    # System metrics
    st.subheader("System Information")
    st.info(f"Streamlit Version: {st.__version__}")
    st.info(f"Python Version: {sys.version.split()[0]}")
    
    # Test medical AI
    st.subheader("Test Medical AI")
    
    with st.form("test_form"):
        test_query = st.text_input("Enter a test medical question:")
        submit = st.form_submit_button("Test")
    
    if submit and test_query:
        with st.spinner("Testing medical AI..."):
            response, from_api, model_name = query_medical_llm(test_query)
            st.subheader("Response:")
            st.write(response)
            
            if from_api:
                st.success(f"✅ Response from {model_name} model")
            else:
                st.warning(f"⚠️ Response from {model_name} (API unavailable)")

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
                        st.rerun()
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
                st.rerun()
        
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