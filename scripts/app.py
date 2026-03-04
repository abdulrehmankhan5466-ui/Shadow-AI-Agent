# scripts/app.py

import streamlit as st
from datetime import datetime
import time

from facts import load_profile, save_profile, learn_new_fact
from llm import get_runnable
from langchain_community.chat_message_histories import ChatMessageHistory

# ────────────────────────────────────────────────
# Config & Session State
# ────────────────────────────────────────────────

if "profile" not in st.session_state:
    st.session_state.profile = load_profile()

if "memory" not in st.session_state:
    st.session_state.memory = ChatMessageHistory()

if "runnable" not in st.session_state:
    st.session_state.runnable = get_runnable(st.session_state.profile, st.session_state.memory)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────

st.sidebar.title("Shadow 💙")
st.sidebar.markdown("Abdulrehman's digital twin")

if st.sidebar.button("Clear Chat & Memory"):
    st.session_state.messages = []
    st.session_state.memory.clear()
    st.rerun()

if st.sidebar.button("What do you know about me?"):
    facts = st.session_state.profile.get("other_facts", [])
    if facts:
        facts_md = "\n".join(f"- {f}" for f in facts)
        msg = f"**What I remember about you so far:**\n\n{facts_md}"
    else:
        msg = "Right now — not much extra stuff saved. Tell me more yaar 😄"
    
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(f"Profile saved to:\n`{st.session_state.profile}`")

# ────────────────────────────────────────────────
# Main Area
# ────────────────────────────────────────────────

st.title("Shadow – Your Digital Twin")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Kya scene hai bro? 😏"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Stream the response
            stream = st.session_state.runnable.stream(
                {"input": prompt},
                config={"configurable": {"session_id": "abdulrehman"}}
            )

            for chunk in stream:
                if hasattr(chunk, "content"):
                    full_response += chunk.content
                    message_placeholder.markdown(full_response + "▌")
                time.sleep(0.01)  # slight delay for smooth feel

            message_placeholder.markdown(full_response)

            # Save assistant reply to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # ── Fact learning logic ──
            lower_prompt = prompt.lower()
            force_save = any(kw in lower_prompt for kw in ["wabloo", "woble", "save this", "remember that"])

            # Very simple keyword-based trigger for now
            fact_keywords = [
                "i like", "i love", "i hate", "i don't like", "i prefer", "my favorite",
                "i am", "my name is", "i work as", "i live in", "i use"
            ]
            should_consider = force_save or any(kw in lower_prompt for kw in fact_keywords)

            if should_consider:
                if learn_new_fact(st.session_state.profile, prompt.strip()):
                    st.info("✅ Saved that as an important fact about you!", icon="🧠")

        except Exception as e:
            error_msg = f"Oops — something broke: {str(e)}\n\nMake sure Ollama is running (`ollama serve`)"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})