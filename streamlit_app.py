import streamlit as st
import requests
import json

# Set page configuration
st.set_page_config(
    page_title="IIT Daya Medical Assistant",
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

# Mockup responses for testing
def get_mock_response(query):
    query_lower = query.lower()
    
    if "ace inhibitor" in query_lower or "hypertension" in query_lower:
        return """
        **Mechanism of Action for ACE Inhibitors in Hypertension Management**
        
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
        **Current Treatment Guidelines for Type 2 Diabetes**
        
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
    else:
        return "I'm providing this response using a mock medical database. To get the most accurate and up-to-date information, you should consult with actual medical professionals and refer to current clinical guidelines."

# Function to call API or use mock response
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
        
        # Let's try different API endpoints
        
        # Writer API endpoint
        writer_endpoint = "https://api.writer.com/v1/generate"
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare payload for Writer API
        writer_payload = {
            "modelId": "palmyra-med-70b-32k",
            "prompt": prompt,
            "temperature": 0.7,
            "maxTokens": 1000
        }
        
        st.session_state['api_debug']['request_to'] = writer_endpoint
        st.session_state['api_debug']['payload'] = writer_payload
        
        try:
            # Make the API request with SSL verification disabled for testing
            writer_response = requests.post(
                writer_endpoint,
                headers=headers,
                json=writer_payload,
                verify=False,  # Disable SSL verification
                timeout=30
            )
            
            st.session_state['api_debug']['status_code'] = writer_response.status_code
            st.session_state['api_debug']['response_preview'] = writer_response.text[:500] if writer_response.text else "No response text"
            
            if writer_response.status_code == 200:
                try:
                    result = writer_response.json()
                    content = result.get('text', '')
                    if content:
                        return content
                    else:
                        st.session_state['api_debug']['error'] = "No content in response"
                except Exception as e:
                    st.session_state['api_debug']['parsing_error'] = str(e)
            
            # If Writer API failed, try NVIDIA NIM endpoint
            nvidia_endpoint = "https://api.nvcf.nvidia.com/v2/llm/completions"
            
            nvidia_payload = {
                "model": "writer/palmyra-med-70b-32k",
                "messages": [
                    {"role": "system", "content": "You are a medical assistant using Palmyra-Med-70B-32K model."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            st.session_state['api_debug']['fallback_request_to'] = nvidia_endpoint
            st.session_state['api_debug']['fallback_payload'] = nvidia_payload
            
            nvidia_response = requests.post(
                nvidia_endpoint,
                headers=headers,
                json=nvidia_payload,
                verify=False,  # Disable SSL verification
                timeout=30
            )
            
            st.session_state['api_debug']['fallback_status_code'] = nvidia_response.status_code
            st.session_state['api_debug']['fallback_response_preview'] = nvidia_response.text[:500] if nvidia_response.text else "No response text"
            
            if nvidia_response.status_code == 200:
                try:
                    result = nvidia_response.json()
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    if content:
                        return content
                    else:
                        st.session_state['api_debug']['fallback_error'] = "No content in response"
                except Exception as e:
                    st.session_state['api_debug']['fallback_parsing_error'] = str(e)
        
        except requests.exceptions.SSLError as ssl_err:
            st.session_state['api_debug']['ssl_error'] = str(ssl_err)
        except Exception as e:
            st.session_state['api_debug']['request_exception'] = str(e)
        
        # If all API calls fail, use mock response with notice
        return "API connection failed. Using mock response instead.\n\n" + get_mock_response(prompt)
        
    except Exception as e:
        st.session_state['api_debug']['exception'] = str(e)
        return f"An error occurred: {str(e)}. Using mock response instead.\n\n" + get_mock_response(prompt)

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
                    response = call_medical_api(prompt)
                    
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
                    response = call_medical_api(prompt)
                    
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