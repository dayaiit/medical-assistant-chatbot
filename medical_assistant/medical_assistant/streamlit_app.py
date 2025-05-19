import streamlit as st
import requests
import os
from PIL import Image
import io
import base64
import time

# Set page configuration
st.set_page_config(
    page_title="Medical Assistant",
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

# Simple user database (in a real app, use a secure database)
users = {
    "doctor1": "password123",
    "doctor2": "password456"
}

# Login page
def login_page():
    st.title("Medical Assistant Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

# Function to call the Palmyra-Med API (mock version for testing)
def call_palmyra_api(prompt):
    # For testing without an API key, return a mock response
    # In production, uncomment the API call code below and add your API key
    
    # Mock response for testing
    time.sleep(2)  # Simulate API delay
    
    if "prescription" in prompt.lower():
        return """
        ## Prescription Analysis
        
        ### Identified Medications and Dosages:
        1. Metformin 500mg - Take 1 tablet twice daily with meals
        2. Lisinopril 10mg - Take 1 tablet daily in the morning
        3. Atorvastatin 20mg - Take 1 tablet daily at bedtime
        
        ### Potential Drug Interactions:
        - No major interactions detected between these medications
        - Monitor blood pressure when taking Lisinopril
        
        ### Usage Considerations:
        - Metformin may cause GI disturbances; take with food to minimize
        - Lisinopril may cause dizziness upon standing
        - Atorvastatin may cause muscle pain in some patients
        
        ### Flags for Review:
        - Consider monitoring kidney function with this medication combination
        - Regular liver function tests recommended with statin therapy
        
        This is an AI analysis and should always be verified by a qualified healthcare professional.
        """
    else:
        # For medical queries
        if "diabetes" in prompt.lower():
            return """
            Based on the query about diabetes management, here are some considerations:
            
            ### Current Guidelines Overview:
            - The ADA's Standards of Medical Care (2024) recommends individualized A1C targets, typically <7% for most patients
            - First-line therapy remains metformin for most patients with Type 2 diabetes
            - GLP-1 receptor agonists and SGLT-2 inhibitors are recommended for patients with cardiovascular disease
            
            ### Key Monitoring Parameters:
            - A1C every 3-6 months
            - Annual comprehensive foot examination
            - Eye examination at diagnosis and then every 1-2 years
            - Regular screening for kidney disease with UACR and eGFR
            
            ### Recent Developments:
            - Tirzepatide (Mounjaro) shows significant benefits for weight loss and glycemic control
            - Increased emphasis on addressing social determinants of health in diabetes management
            - Greater focus on technology integration for monitoring and management
            
            Would you like more specific information about any particular aspect of diabetes management?
            """
        elif "hypertension" in prompt.lower():
            return """
            Regarding hypertension management:
            
            ### Current Guidelines Summary:
            - Target BP <130/80 mmHg for most patients according to ACC/AHA guidelines
            - First-line treatments include thiazide diuretics, ACE inhibitors, ARBs, and CCBs
            - Lifestyle modifications remain foundational (DASH diet, sodium restriction, physical activity)
            
            ### Diagnostic Considerations:
            - Confirm with out-of-office measurements when possible
            - Consider secondary causes if resistant to treatment or early-onset
            - Evaluate for target organ damage (heart, kidneys, eyes)
            
            ### Treatment Strategy:
            - Begin with single agent for stage 1, consider dual therapy for stage 2
            - Combination pills may improve adherence
            - Consider patient comorbidities when selecting agents
            
            ### Monitoring:
            - Follow-up within 1 month for medication adjustments
            - Monitor electrolytes and kidney function with RAAS inhibitors
            - Encourage home BP monitoring for most patients
            
            This analysis is for clinical consideration and should be applied within the context of the individual patient's needs and circumstances.
            """
        else:
            return """
            Thank you for your medical query. As an AI medical assistant, I can provide general information based on medical literature, but clinical judgment is essential.
            
            The information available suggests considering the following aspects:
            
            1. Differential diagnoses to consider based on the presented symptoms
            2. Recommended diagnostic approach according to current guidelines
            3. Evidence-based treatment options for the most likely conditions
            4. Key monitoring parameters and follow-up recommendations
            
            For more specific guidance, additional clinical details would be helpful, including:
            - Duration and progression of symptoms
            - Relevant past medical history
            - Current medications
            - Results of any preliminary investigations
            
            Would you like me to elaborate on any particular aspect of this analysis?
            """
    
    # Production code (uncomment and add your API key when ready)
    """
    api_key = "YOUR_WRITER_API_KEY_HERE"  # In production, use st.secrets["WRITER_API_KEY"]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "palmyra-med-70b-32k",
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(
            "https://api.writer.com/v1/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json().get('choices', [{}])[0].get('text', '')
        else:
            return f"Error: API returned status code {response.status_code}"
            
    except Exception as e:
        return f"An error occurred: {str(e)}"
    """

# Check for emergency keywords
def check_for_emergency(text):
    emergency_keywords = [
        "emergency", "urgent", "severe", "critical", "life-threatening", 
        "heart attack", "stroke", "seizure", "unconscious", "not breathing",
        "suicide", "hemorrhage", "bleeding severely"
    ]
    
    for keyword in emergency_keywords:
        if keyword.lower() in text.lower():
            return True
    return False

# Extract text from image (mock function for demo)
def extract_text_from_image(image):
    # In a real application, you would use pytesseract here
    # For the demo, return mock prescription text
    return """
    Dr. John Smith, MD
    123 Medical Plaza
    Phone: (555) 123-4567
    
    Patient: Jane Doe
    Date: 05/15/2025
    
    Rx:
    
    1. Metformin 500mg
       Sig: 1 tablet PO BID with meals
       Disp: 60 tablets
       Refills: 3
    
    2. Lisinopril 10mg
       Sig: 1 tablet PO daily in AM
       Disp: 30 tablets
       Refills: 3
    
    3. Atorvastatin 20mg
       Sig: 1 tablet PO qHS
       Disp: 30 tablets
       Refills: 3
    
    Signed: Dr. John Smith, MD
    """

# Main application
def main_app():
    st.title(f"Medical Assistant - Welcome, {st.session_state.username}")
    
    # Disclaimer
    st.warning("**Important:** This tool is for healthcare professionals only. All AI-generated responses should be reviewed by qualified medical personnel. Not intended for direct patient use.")
    
    # Sidebar
    with st.sidebar:
        st.header("Options")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.messages = []
            st.experimental_rerun()
        
        st.header("Prescription Analysis")
        uploaded_file = st.file_uploader("Upload a prescription", type=["jpg", "jpeg", "png", "pdf"])
        
        if uploaded_file is not None:
            if st.button("Analyze Prescription"):
                # Display uploaded prescription
                if uploaded_file.type.startswith('image'):
                    st.image(uploaded_file, caption="Uploaded Prescription", use_column_width=True)
                
                # Process the prescription
                try:
                    if uploaded_file.type.startswith('image'):
                        image = Image.open(uploaded_file)
                        prescription_text = extract_text_from_image(image)
                    else:
                        # For PDF you would need additional processing
                        prescription_text = "PRESCRIPTION SAMPLE TEXT FOR PDF"
                        
                    # Create a prompt for prescription analysis
                    prompt = f"""I am a medical assistant powered by AI. I'm analyzing a prescription that contains the following text:
                    
                    {prescription_text}
                    
                    Please analyze this prescription and provide:
                    1. Identified medications and dosages
                    2. Potential drug interactions if obvious
                    3. Standard usage considerations
                    4. Any potential flags that a doctor should review
                    
                    Note: This is an AI analysis and should always be verified by a qualified healthcare professional."""
                    
                    with st.spinner("Analyzing prescription..."):
                        analysis = call_palmyra_api(prompt)
                        st.session_state.messages.append({"role": "user", "content": f"Analyzed prescription: {uploaded_file.name}"})
                        st.session_state.messages.append({"role": "assistant", "content": analysis})
                
                except Exception as e:
                    st.error(f"Error processing prescription: {str(e)}")
    
    # Chat interface
    st.header("Medical Chat Assistant")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    user_input = st.chat_input("Type your medical question here...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Check for emergency
        if check_for_emergency(user_input):
            emergency_response = """
            ⚠️ **POTENTIAL EMERGENCY DETECTED** ⚠️
            
            This appears to describe an emergency situation that requires immediate medical attention. 
            
            Please call emergency services (911) immediately or proceed to the nearest emergency room.
            
            This AI assistant is not a substitute for emergency medical care.
            """
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(emergency_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": emergency_response})
        else:
            # Create a structured prompt for medical context
            prompt = f"""I am a medical assistant powered by AI. I'm designed to help medical professionals 
            with preliminary analysis. I do not provide medical advice directly to patients.
            
            Medical professional's query: {user_input}
            
            Please provide a thoughtful analysis, potential considerations, and relevant medical information:"""
            
            # Get response from API
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = call_palmyra_api(prompt)
                    st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

# Main logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
