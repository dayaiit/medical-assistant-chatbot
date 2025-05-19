import streamlit as st
import requests
import json

# Set page title and icon
st.set_page_config(
    page_title="Dr. Daya's Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

# Add a nice title
st.title("Dr. Daya's Clinic Medical Assistant")
st.write("Ask me any medical questions and I'll help you find answers!")

# Add a sidebar with information
with st.sidebar:
    st.header("About")
    st.write("This medical assistant can help answer medical questions for healthcare professionals.")
    
    st.header("Users")
    st.write("• Doctors")
    st.write("• Nurses")
    st.write("• Pharmacists")
    st.write("• Clinical Manager")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to get AI response
def get_medical_response(question):
    # This function creates a mock response since we're having API issues
    
    if "fever" in question.lower():
        return """
        # About Fever
        
        A fever is a temporary increase in body temperature, often due to an illness. Having a fever is a sign that something out of the ordinary is going on in your body.
        
        ## Normal Body Temperature & Fever
        - Normal body temperature is around 98.6°F (37°C)
        - A fever is usually defined as:
          - Adults: 100.4°F (38°C) or higher
          - Children: 100.4°F (38°C) or higher
        
        ## Common Causes
        - Infections (viral, bacterial)
        - Inflammatory conditions
        - Medications
        - Immunizations
        
        ## Treatment Approaches
        - Rest and hydration
        - Over-the-counter medications like acetaminophen or ibuprofen
        - Cooling measures for high fevers
        
        Always consult a healthcare provider for persistent or high fevers.
        """
    
    elif "diabetes" in question.lower():
        return """
        # Diabetes Overview
        
        Diabetes is a chronic health condition that affects how your body turns food into energy.
        
        ## Types of Diabetes
        - **Type 1 Diabetes**: The body doesn't produce insulin
        - **Type 2 Diabetes**: The body doesn't use insulin properly
        - **Gestational Diabetes**: Develops during pregnancy
        
        ## Common Symptoms
        - Increased thirst and urination
        - Extreme hunger
        - Unexplained weight loss
        - Fatigue
        - Blurred vision
        
        ## Management
        - Regular blood sugar monitoring
        - Insulin therapy (for Type 1)
        - Oral medications (often for Type 2)
        - Diet and exercise
        - Regular medical check-ups
        
        Early detection and treatment can decrease the risk of developing complications.
        """
    
    elif "heart" in question.lower() or "cardiac" in question.lower():
        return """
        # Heart Health
        
        The heart is a muscular organ that pumps blood throughout the body.
        
        ## Heart Disease Risk Factors
        - High blood pressure
        - High cholesterol
        - Smoking
        - Diabetes
        - Obesity
        - Physical inactivity
        - Family history
        
        ## Common Heart Conditions
        - Coronary artery disease
        - Heart failure
        - Arrhythmias
        - Valve disorders
        
        ## Prevention
        - Regular exercise (150 minutes/week recommended)
        - Healthy diet rich in fruits, vegetables, whole grains
        - Avoiding smoking
        - Limiting alcohol
        - Managing stress
        - Regular health screenings
        
        Early intervention can significantly improve outcomes for heart conditions.
        """
    
    else:
        return f"""
        # Medical Information
        
        Thank you for your question about "{question}".
        
        This would normally be answered by connecting to the Palmyra-Med-70B-32k medical AI model, but we're currently using a local response system while we resolve API connection issues.
        
        ## General Medical Advice
        
        - Always consult healthcare professionals for medical concerns
        - Follow evidence-based medical guidelines
        - Stay up-to-date with current medical literature
        - Consider patient-specific factors in all medical decisions
        
        Would you like to ask about specific topics like fever, diabetes, or heart health?
        """

# Chat input
user_question = st.chat_input("Type your medical question here")

# Process the user's question
if user_question:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
    
    # Get and display AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_medical_response(user_question)
            st.markdown(response)
    
    # Add AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})