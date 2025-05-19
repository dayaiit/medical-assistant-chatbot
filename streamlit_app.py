import streamlit as st
import requests
import json

# Set page configuration
st.set_page_config(
    page_title="Dr. Daya's Medical Assistant",
    page_icon="🩺",
    layout="wide"
)

# Add custom styling
st.markdown("""
<style>
    .main-title {
        color: #2E6EA6;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #e6f3ff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .assistant-message {
        background-color: #f0fff0;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #2E6EA6;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        color: #666;
        font-size: 14px;
    }
    .disclaimer {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 10px;
        margin-bottom: 20px;
        border-radius: 5px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Initialization
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""

# User database - Customize for your clinic staff
users = {
    "doctor1": "password123",
    "doctor2": "password456",
    "doctor3": "password789",
    "doctor4": "password101",
    "doctor5": "password102",
    "nurse1": "nursepass1",
    "nurse2": "nursepass2",
    "nurse3": "nursepass3",
    "nurse4": "nursepass4",
    "nurse5": "nursepass5",
    "nurse6": "nursepass6",
    "nurse7": "nursepass7",
    "pharmacist": "pharmpass1",
    "manager": "managerpass1",
    "drdaya": "admin123"  # Your admin account
}

# Backup mock responses for when the API fails
def get_mock_response(query):
    query_lower = query.lower()
    
    if "prescription" in query_lower or "analyze" in query_lower:
        return """
        ## Prescription Analysis

        ### Medications Identified:
        1. **Metformin 500mg** - Oral antihyperglycemic agent
           - Dosage: 1 tablet twice daily with meals
           - Purpose: Management of type 2 diabetes

        2. **Lisinopril 10mg** - ACE inhibitor
           - Dosage: 1 tablet daily in the morning
           - Purpose: Treatment of hypertension

        3. **Atorvastatin 20mg** - HMG-CoA reductase inhibitor (statin)
           - Dosage: 1 tablet daily at bedtime
           - Purpose: Management of hyperlipidemia

        ### Potential Interactions:
        - No significant interactions between these medications
        - Lisinopril may enhance the hypoglycemic effect of Metformin (monitor blood glucose)

        ### Clinical Considerations:
        - All three medications align with standard treatment protocols
        - Appropriate dosing for an adult patient
        - Regular monitoring recommended:
          - HbA1c every 3-6 months (Metformin)
          - Blood pressure checks (Lisinopril)
          - Lipid panel every 6-12 months (Atorvastatin)
          - Renal and liver function tests periodically

        ### Additional Recommendations:
        - Consider kidney function monitoring due to combined use of Metformin and Lisinopril
        - Monitor for muscle pain or weakness (potential statin side effect)
        - Ensure patient is educated about hypoglycemia symptoms
        """
    elif "ace inhibitor" in query_lower or "hypertension" in query_lower:
        return """
        ## Mechanism of Action for ACE Inhibitors in Hypertension Management

        ACE (Angiotensin-Converting Enzyme) inhibitors work by blocking the conversion of angiotensin I to angiotensin II, which is a potent vasoconstrictor. Here's the detailed mechanism:

        1. **RAAS Pathway Inhibition**: ACE inhibitors block the renin-angiotensin-aldosterone system (RAAS) by preventing the conversion of angiotensin I to angiotensin II.

        2. **Decreased Vasoconstriction**: With less angiotensin II, there is reduced vasoconstriction of blood vessels, leading to vasodilation and decreased peripheral vascular resistance.

        3. **Reduced Aldosterone Production**: Angiotensin II stimulates aldosterone release from the adrenal cortex. By reducing angiotensin II, ACE inhibitors decrease aldosterone production, leading to decreased sodium and water retention.

        4. **Bradykinin Accumulation**: ACE inhibitors also prevent the breakdown of bradykinin, a vasodilator. Increased bradykinin levels contribute to the blood pressure-lowering effect through additional vasodilation.

        5. **Improved Endothelial Function**: ACE inhibitors improve endothelial function by increasing nitric oxide production and reducing oxidative stress.

        6. **Cardiac and Vascular Remodeling**: Long-term use prevents pathological cardiac and vascular remodeling, reducing left ventricular hypertrophy and arterial wall thickening.

        7. **Renoprotective Effects**: ACE inhibitors dilate both afferent and efferent arterioles in the kidney, reducing intraglomerular pressure and providing renoprotection.

        These mechanisms make ACE inhibitors effective first-line agents for hypertension management, particularly beneficial for patients with comorbid conditions like heart failure, post-myocardial infarction, diabetic nephropathy, and proteinuric kidney disease.
        """
    elif "diabetes" in query_lower:
        return """
        ## Current Treatment Guidelines for Type 2 Diabetes

        The latest guidelines for managing type 2 diabetes emphasize a patient-centered approach with these key components:

        1. **Glycemic Targets**: Individualized A1C targets, typically <7% for most patients, but can range from <6.5% to <8% based on patient factors.

        2. **First-line Therapy**: Metformin remains the preferred initial pharmacologic agent unless contraindicated.

        3. **Cardiovascular Risk Reduction**: For patients with established ASCVD or high risk, GLP-1 receptor agonists or SGLT-2 inhibitors with proven cardiovascular benefit are recommended regardless of A1C levels.

        4. **Combination Therapy**: Early combination therapy should be considered in patients with A1C ≥1.5% above target.

        5. **SGLT-2 Inhibitors**: Specifically recommended for patients with heart failure with reduced ejection fraction (HFrEF) or chronic kidney disease (CKD).

        6. **Injectable Medications**: GLP-1 receptor agonists are generally preferred over insulin as the first injectable medication.

        7. **Comprehensive Approach**: Treatment should include lifestyle modification (medical nutrition therapy, physical activity), patient education, and addressing cardiovascular risk factors.

        8. **Technology Integration**: Continuous glucose monitoring (CGM) is recommended for most patients on intensive insulin regimens.

        9. **Regular Monitoring**: A1C testing every 3-6 months, annual comprehensive foot examinations, eye examinations, and screening for kidney disease.

        10. **Social Determinants of Health**: Guidelines now emphasize addressing social determinants like food insecurity, housing stability, and health literacy.

        These recommendations are based on the latest clinical evidence and consensus from major diabetes organizations.
        """
    elif "statin" in query_lower or "cholesterol" in query_lower:
        return """
        ## Mechanism of Action and Clinical Use of Statins

        Statins (HMG-CoA reductase inhibitors) are first-line agents for managing hyperlipidemia and reducing cardiovascular risk.

        ### Mechanism of Action:
        1. **Enzyme Inhibition**: Statins competitively inhibit HMG-CoA reductase, the rate-limiting enzyme in cholesterol biosynthesis in the liver.
        
        2. **LDL Receptor Upregulation**: Reduced intracellular cholesterol leads to upregulation of LDL receptors on hepatocyte cell surfaces, increasing LDL-C clearance from the bloodstream.
        
        3. **Pleiotropic Effects**: Statins also exhibit anti-inflammatory, antithrombotic, and endothelial function-improving properties independent of their lipid-lowering effects.

        ### Clinical Indications:
        - Primary and secondary prevention of ASCVD
        - Familial hypercholesterolemia
        - Diabetes with cardiovascular risk factors
        - Elevated coronary artery calcium scores

        ### Efficacy:
        - LDL-C reduction: 20-60% depending on the statin and dose
        - HDL-C increase: 5-15%
        - Triglyceride reduction: 7-30%
        - Relative risk reduction for major cardiovascular events: approximately 20-25%

        ### Monitoring:
        - Baseline liver function tests and lipid panel
        - Follow-up lipid panel 4-12 weeks after initiation
        - Liver function monitoring not routinely required unless clinically indicated
        - Monitor for myalgia and other side effects

        ### Side Effects:
        - Myalgia and myopathy (most common)
        - Elevated liver enzymes (rare)
        - New-onset diabetes (slight increased risk)
        - Rhabdomyolysis (very rare)

        The benefit of ASCVD risk reduction substantially outweighs potential risks in most patients with clear indications.
        """
    else:
        return """
        I'm providing this response based on standard medical knowledge and guidelines. For this specific query, I would need to connect to the Palmyra-Med-70B-32K API to provide a more detailed, specialized response. 

        For the most accurate and up-to-date information, please consult with appropriate medical references and clinical guidelines relevant to this specific topic.
        """

# Function to call API without SSL verification
def call_medical_api(prompt):
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
            return "API key not configured. Using mock response instead.\n\n" + get_mock_response(prompt)
        
        # Correct NVIDIA API endpoint and model ID
        api_endpoint = "https://integrate.api.nvidia.com/v1"
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Correct payload format
        payload = {
            "model": "ai-palmyra-med-70b",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1000
        }
        
        st.session_state['api_debug']['endpoint'] = api_endpoint
        st.session_state['api_debug']['payload'] = payload
        
        # Create session with SSL verification disabled if needed
        session = requests.Session()
        
        # First try with SSL verification
        try:
            response = session.post(
                api_endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
        except requests.exceptions.SSLError:
            # If SSL verification fails, try without it (with warning)
            st.session_state['api_debug']['ssl_error'] = "SSL verification failed, trying without verification"
            
            # Suppress SSL warnings
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Retry without SSL verification
            response = session.post(
                api_endpoint,
                headers=headers,
                json=payload,
                timeout=30,
                verify=False
            )
        
        st.session_state['api_debug']['status_code'] = response.status_code
        st.session_state['api_debug']['response_preview'] = response.text[:200] if response.text else "No response"
        
        if response.status_code == 200:
            try:
                result = response.json()
                # Extract content based on correct response format
                if 'choices' in result and len(result['choices']) > 0:
                    if 'message' in result['choices'][0] and 'content' in result['choices'][0]['message']:
                        return result['choices'][0]['message']['content']
                    elif 'text' in result['choices'][0]:
                        return result['choices'][0]['text']
                else:
                    st.session_state['api_debug']['unexpected_format'] = "Response format not recognized"
                    st.session_state['api_debug']['full_response'] = str(result)[:500]
            except Exception as e:
                st.session_state['api_debug']['parsing_error'] = str(e)
        else:
            st.session_state['api_debug']['error_response'] = response.text
        
        # Fall back to mock response if API call fails
        return "API connection failed. Using mock response instead.\n\n" + get_mock_response(prompt)
        
    except Exception as e:
        st.session_state['api_debug']['exception'] = str(e)
        return f"An error occurred: {str(e)}. Using mock response instead.\n\n" + get_mock_response(prompt)
# Login page
def login_page():
    st.markdown('<h1 class="main-title">Dr. Daya\'s Clinic Medical Assistant</h1>', unsafe_allow_html=True)
    
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
    
    st.markdown('<div class="footer">© 2025 Dr. Daya\'s Clinic. Powered by Palmyra-Med-70B-32K. For authorized medical staff only.</div>', unsafe_allow_html=True)

# Main application
def main_app():
    st.markdown('<h1 class="main-title">Dr. Daya\'s Clinic Medical Assistant</h1>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="disclaimer">Welcome, <b>{st.session_state.username}</b>! This tool is for healthcare professionals only. All AI-generated responses should be reviewed by qualified medical personnel. Not intended for direct patient use.</div>', unsafe_allow_html=True)
    
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
                    prompt = f"""
                    I am a medical professional analyzing a prescription image. I need a detailed analysis including:
                    1. Medications identified and their dosages
                    2. Purpose of each medication
                    3. Potential drug interactions
                    4. Clinical considerations and monitoring recommendations
                    5. Any concerns or issues that should be reviewed
                    
                    Please provide a structured, comprehensive analysis suitable for healthcare professionals.
                    """
                    
                    # Get API response
                    response = call_medical_api(prompt)
                    
                    # Add to chat history
                    st.session_state.messages.append({"role": "user", "content": f"Analyzed prescription: {uploaded_file.name}"})
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
    
    # Chat interface
    st.header("Medical Assistant")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message"><b>Assistant:</b> {message["content"]}</div>', unsafe_allow_html=True)
    
    # User input
    user_input = st.text_input("Type your medical question here...")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Send"):
            if user_input:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Create a structured prompt for medical context
                prompt = f"""
                As a healthcare professional, I need information about: {user_input}
                
                Please provide a detailed, evidence-based response suitable for medical professionals. Include relevant clinical guidelines, mechanisms of action, and practical considerations where appropriate.
                """
                
                # Call the API with a loading spinner
                with st.spinner("Generating response..."):
                    response = call_medical_api(prompt)
                    
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    # Debug information section (only visible to the admin account)
    if st.session_state.username == "drdaya":
        if st.checkbox("Show API debug info", False):
            st.write("### API Debug Information")
            if 'api_debug' in st.session_state:
                st.json(st.session_state['api_debug'])
    
    # Footer
    st.markdown('<div class="footer">© 2025 Dr. Daya\'s Clinic. Powered by Palmyra-Med-70B-32K.<br>For authorized medical staff only.</div>', unsafe_allow_html=True)

# Main logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()