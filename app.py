# app.py
import streamlit as st
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate,)

# Import our custom prompts and avatar data
from prompts import PERSONALITIES, AVATARS

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="AI Dating Companion",  page_icon="❤️",  layout="centered",)

# Function to load our custom CSS for animations
def load_local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_local_css("static/style.css")

# --- 2. API KEY & AI CHAIN SETUP ---
# Load the API key from the .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def setup_ai_chain(personality_name="Seductive Tease"):
    """Sets up the main AI conversation chain."""
    # Define the AI model
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.8, openai_api_key=openai_api_key)
    # Setup memory to remember the last 5 exchanges
    memory = ConversationBufferWindowMemory(k=5, return_messages=True)
    # Get the system prompt from our prompts.py file
    system_prompt = PERSONALITIES[personality_name]["system_prompt"]
    # Create the final prompt structure
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    # Build the chain
    chain = ConversationChain(llm=llm, memory=memory, prompt=prompt, verbose=False)
    return chain

# --- 3. SESSION STATE ---
# This is where we store data that needs to persist during the user's session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chain" not in st.session_state:
    # For Phase 1, we are locking the personality to "Seductive Tease"
    st.session_state.chain = setup_ai_chain("Seductive Tease")

# --- 4. UI & INTERACTION ---

# Display the title and the animated avatar
st.title("AI Companion: Lilith")
st.markdown(f'<img src="{AVATARS["Seductive Tease"]}" class="breathing-avatar">', unsafe_allow_html=True)
st.markdown("  
", unsafe_allow_html=True) # A little space

# Display the 18+ disclaimer
st.warning("**Disclaimer:** This is an AI chatbot for adult audiences (18+). It is not a real person. Please interact responsibly.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get and display AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chain.run(prompt)
            st.markdown(response)
    
    # Add AI response to history
    st.session_state.messages.append({"role": "assistant", "content": response})

