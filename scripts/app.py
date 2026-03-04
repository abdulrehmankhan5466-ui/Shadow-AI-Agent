import streamlit as st
from datetime import datetime
import time

from facts import load_profile, learn_new_fact, PROFILE_FILE
from llm import get_runnable
from langchain_community.chat_message_histories import ChatMessageHistory

# ────────────────────────────────────────────────
# Session State
# ────────────────────────────────────────────────

if "profile" not in st.session_state:
    st.session_state.profile = load_profile()

if "memory" not in st.session_state:
    st.session_state.memory = ChatMessageHistory()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "language_mode" not in st.session_state:
    st.session_state.language_mode = "English"   # default changed to English

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.85

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True

# Re-create runnable when needed
if ("runnable" not in st.session_state or
    st.session_state.get("last_lang") != st.session_state.language_mode or
    st.session_state.get("last_temp") != st.session_state.temperature or
    st.session_state.get("last_memory") != st.session_state.memory_enabled):

    st.session_state.runnable = get_runnable(
        st.session_state.profile,
        st.session_state.memory if st.session_state.memory_enabled else ChatMessageHistory(),
        st.session_state.language_mode,
        st.session_state.temperature
    )
    st.session_state.last_lang = st.session_state.language_mode
    st.session_state.last_temp = st.session_state.temperature
    st.session_state.last_memory = st.session_state.memory_enabled

# ────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────

st.sidebar.title("Shadow 💙")
st.sidebar.markdown("Abdulrehman's Shadow")

# Debug facts count
st.sidebar.caption(f"Loaded facts: {len(st.session_state.profile.get('other_facts', []))}")

if st.sidebar.button("Preview all saved facts"):
    facts = st.session_state.profile.get("other_facts", [])
    if facts:
        st.sidebar.markdown("\n".join(f"- {f}" for f in facts))
    else:
        st.sidebar.warning("No facts loaded — check the JSON file")

# Memory toggle
st.sidebar.toggle(
    "Use conversation memory",
    value=st.session_state.memory_enabled,
    key="memory_toggle",
    help="When ON → remembers previous messages in this chat\nWhen OFF → treats every message as new (facts still safe)"
)
st.session_state.memory_enabled = st.session_state.memory_toggle

# Language selector – simple & reliable
st.sidebar.radio(
    "Reply language",
    options=["English", "Urdu", "Mix"],
    index=["English", "Urdu", "Mix"].index(st.session_state.language_mode),
    key="lang_radio",
    horizontal=True
)
st.session_state.language_mode = st.session_state.lang_radio

# Temperature
st.sidebar.slider(
    "Creativity (temperature)",
    0.6, 1.2, st.session_state.temperature, 0.05,
    key="temp_slider"
)
st.session_state.temperature = st.session_state.temp_slider

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("Clear All", use_container_width=True):
        st.session_state.messages = []
        st.session_state.memory.clear()
        st.rerun()

if st.sidebar.button("What I remember about you"):
    facts = st.session_state.profile.get("other_facts", [])
    if facts:
        facts_md = "\n".join(f"• {f}" for f in facts)
        msg = f"**What I remember about you:**\n\n{facts_md}"
    else:
        msg = "Nothing extra saved yet — tell me more yaar 😄"

    # Prevent duplicate messages
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != msg:
        st.session_state.messages.append({"role": "assistant", "content": msg})
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(f"Profile: {PROFILE_FILE}")

# ────────────────────────────────────────────────
# Main area
# ────────────────────────────────────────────────

st.title("Shadow: Abdulrehman's Shadow 💙")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("What's up yaar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = st.session_state.runnable.stream(
                {"input": prompt},
                config={"configurable": {"session_id": "abdulrehman"}}
            )

            for chunk in stream:
                if hasattr(chunk, "content"):
                    full_response += chunk.content
                    message_placeholder.markdown(full_response + "▌")
                time.sleep(0.015)

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Fact learning
            lower = prompt.lower()
            force = any(x in lower for x in ["wabloo", "save this", "remember that"])
            triggers = ["i like", "i love", "i hate", "i don't like", "my favorite", "مجھے پسند ہے", "مجھے پسند نہیں"]
            if force or any(t in lower for t in triggers):
                if learn_new_fact(st.session_state.profile, prompt.strip()):
                    st.info("✅ Saved as important fact!", icon="🧠")
                    st.rerun()

        except Exception as e:
            err = f"Something went wrong: {str(e)}\nMake sure Ollama is running (`ollama serve`)"
            st.error(err)
            st.session_state.messages.append({"role": "assistant", "content": err})