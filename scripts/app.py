# scripts/app.py - SHADOW AI in STREAMLIT - FULL WORKING VERSION

import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import io
import base64

# Import your existing modules
from facts import load_profile, save_profile, learn_new_fact
from llm import get_runnable, ChatMessageHistory

# Config
DATA_DIR = r"D:\Shadow-AI-Companion\data"
PROFILE_FILE = os.path.join(DATA_DIR, 'user_profile.json')
ASSETS_DIR = r"D:\Shadow-AI-Companion\scripts\assets"

# Load profile
if "profile" not in st.session_state:
    st.session_state.profile = load_profile()

# Memory for chat
if "memory" not in st.session_state:
    st.session_state.memory = ChatMessageHistory()

# Runnable (LLM)
if "runnable" not in st.session_state:
    st.session_state.runnable = get_runnable(st.session_state.profile, st.session_state.memory)

# Chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
st.sidebar.title("Shadow")
st.sidebar.markdown("Abdulrehman's AI")

if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.memory.clear()
    st.rerun()

if st.sidebar.button("What do you know about me?"):
    facts = "\n".join(f"- {f}" for f in st.session_state.profile["other_facts"]) if st.session_state.profile["other_facts"] else "Nothing special yet — tell me more!"
    st.session_state.messages.append({"role": "assistant", "content": f"**What I know about you so far:**\n\n{facts}"})
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Facts saved to:**")
st.sidebar.code(PROFILE_FILE, language="text")

# Main chat area
st.title("Shadow – Abdulrehman's AI Companion")

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What’s on your mind?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Show typing indicator
    with st.chat_message("assistant"):
        with st.spinner("Shadow is thinking..."):
            try:
                response = st.session_state.runnable.invoke(
                    {"input": prompt},
                    config={"configurable": {"session_id": "abdulrehman"}}
                ).content.strip()

                st.markdown(response)

                # Fact learning
                save_trigger = "wabloo" in prompt.lower() or "woble" in prompt.lower()
                has_fact_words = any(word in prompt.lower() for word in ["like", "love", "hate", "don't like", "prefer", "favorite", "dislike", "my name", "i am", "i work"])

                if save_trigger or has_fact_words:
                    fact = prompt.strip()
                    if learn_new_fact(st.session_state.profile, fact):
                        st.info(f"Saved as important fact! ✅\n\"{fact}\"")
                        st.rerun()

                # Add to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                error_msg = f"Error: {str(e)}\nMake sure Ollama is running (`ollama serve`)"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.caption("Shadow – Abdulrehman's AI Companion | Built with Streamlit & Ollama")