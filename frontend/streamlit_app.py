import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Streamlit page config
st.set_page_config(
    page_title="TailorTalk - Calendar Booking Assistant",
    page_icon="📅",
    layout="centered"
)

# Header
st.title("📅 TailorTalk")
st.subheader("Your AI-Powered Calendar Booking Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "👋 Hello! I'm TailorTalk, your calendar booking assistant. How can I help you today?"
    })

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"message": prompt},
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    bot_response = response.json()["response"]
                    st.write(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                else:
                    error_msg = f"Error: {response.status_code}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
            except requests.exceptions.ConnectionError:
                error_msg = "Cannot connect to backend. Make sure the backend is running."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "👋 Hello! I'm TailorTalk, your calendar booking assistant. How can I help you today?"
    }]
    st.rerun()