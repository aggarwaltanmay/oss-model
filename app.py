import streamlit as st
import os
from dotenv import load_dotenv
from models import OpenSourceAssistant, FrontierAssistant

# Load environment variables
load_dotenv()

st.set_page_config(page_title="AI Personal Assistants", page_icon="🤖", layout="centered")

st.title("🤖 AI Personal Assistants")

# Sidebar setup
st.sidebar.title("Configuration")

assistant_type = st.sidebar.radio(
    "Select Assistant:",
    ("Open Source Local (Qwen 2.5 0.5B)", "Frontier Model (Gemini 2.5 Flash)")
)

st.sidebar.markdown("---")
st.sidebar.subheader("API Keys")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))

st.sidebar.markdown("---")
st.sidebar.info("The Open Source assistant runs entirely locally! You only need an API key for the Frontier model.")

# Initialize session state for messages for both models separately
if "messages_os" not in st.session_state:
    st.session_state.messages_os = [
        {"role": "system", "content": "You are a helpful AI personal assistant. Be concise and friendly."}
    ]
if "messages_fr" not in st.session_state:
    st.session_state.messages_fr = [
        {"role": "system", "content": "You are a helpful AI personal assistant. Be concise and friendly."}
    ]

# Determine which messages array to use
if "Open Source" in assistant_type:
    current_messages = st.session_state.messages_os
    model_name = "Open Source Assistant"
else:
    current_messages = st.session_state.messages_fr
    model_name = "Frontier Assistant"

# Display chat history (skipping the system message)
for message in current_messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input(f"Message {model_name}..."):
    # Append user message to state
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            if "Open Source" in assistant_type:
                # No API key needed, it runs locally via transformers
                if "local_assistant" not in st.session_state:
                    with st.spinner("Downloading/Loading 0.5B Model locally..."):
                        st.session_state.local_assistant = OpenSourceAssistant()
                assistant = st.session_state.local_assistant
            else:
                if not gemini_key:
                    st.error("Please provide a Gemini API Key in the sidebar.")
                    st.stop()
                assistant = FrontierAssistant(api_key=gemini_key)
            
            with st.spinner("Thinking..."):
                response = assistant.generate_response(current_messages)
            
            message_placeholder.markdown(response)
            current_messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
