import streamlit as st
import os
from writerai import Writer

# Page setup
st.set_page_config(page_title="Medical Assistant Chatbot", layout="wide")

# Add title and description
st.title("Medical Assistant Chatbot")
st.write("Ask medical questions or upload prescriptions for analysis")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to get response from Writer API
def get_medical_response(question):
    try:
        # Try to use the Writer API
        client = Writer(api_key=st.secrets["WRITER_API_KEY"])
        
        # Send question to the Palmyra-Med-70B-32k model
        chat_completion = client.chat.chat(
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful medical assistant providing accurate information to healthcare professionals."
                },
                {
                    "role": "user", 
                    "content": question
                }
            ],
            model="palmyra-med-70b-32k",
            temperature=0.3,
            max_tokens=800
        )
        
        # Get the response text
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        # If there's an error, use a fallback response
        st.error(f"Error connecting to medical AI: {str(e)}")
        return f"I'm currently unable to access my medical knowledge database. Here's a general response: Medical questions about '{question}' should be addressed by consulting official medical resources or healthcare providers."

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Get user input
user_question = st.chat_input("Type your medical question here")

# Handle user input
if user_question:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_question})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_question)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_medical_response(user_question)
            st.write(response)
    
    # Add AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})