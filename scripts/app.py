import streamlit as st
from datetime import datetime
import time

from facts import load_profile, learn_new_fact
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
    st.session_state.language_mode = "Mix"  # default: natural Urdu-English mix

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.8

# Re-create runnable when language or temp changes
if "runnable" not in st.session_state or \
   "last_lang" not in st.session_state or \
   "last_temp" not in st.session_state or \
   st.session_state.last_lang != st.session_state.language_mode or \
   st.session_state.last_temp != st.session_state.temperature:

    st.session_state.runnable = get_runnable(
        st.session_state.profile,
        st.session_state.memory,
        st.session_state.language_mode,
        st.session_state.temperature
    )
    st.session_state.last_lang = st.session_state.language_mode
    st.session_state.last_temp = st.session_state.temperature

# ────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────

st.sidebar.title("Shadow 💙")
st.sidebar.markdown("Abdulrehman کا ڈیجیٹل ٹوئن")

# Language choice
st.sidebar.subheader("زبان / Language")
lang = st.sidebar.radio(
    "Shadow کس زبان میں بات کرے؟",
    options=["English", "Urdu", "Mix (Urdu + English)"],
    index=["English", "Urdu", "Mix (Urdu + English)"].index(st.session_state.language_mode),
    key="lang_radio"
)
st.session_state.language_mode = {"English": "English", "Urdu": "Urdu", "Mix (Urdu + English)": "Mix"}[lang]

# Temperature control
st.sidebar.subheader("Creativity")
st.session_state.temperature = st.sidebar.slider(
    "Temperature (creativity level)",
    0.6, 1.2, st.session_state.temperature, 0.05,
    help="Lower = more focused & safe\nHigher = more creative & random"
)

if st.sidebar.button("🆕 New Chat (Clear messages only)"):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("Clear Everything (Memory + Chat)"):
    st.session_state.messages = []
    st.session_state.memory.clear()
    st.rerun()

if st.sidebar.button("What do you know about me?"):
    facts = st.session_state.profile.get("other_facts", [])
    if facts:
        facts_md = "\n".join(f"- {f}" for f in facts)
        msg = f"**جو میں تیرے بارے میں جانتا ہوں:**\n\n{facts_md}"
    else:
        msg = "ابھی زیادہ کچھ خاص سیو نہیں ہوا یار۔ کچھ بتا نا 😄"
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Profile → data/user_profile.json")

# ────────────────────────────────────────────────
# Main Area
# ────────────────────────────────────────────────

st.title("Shadow – Abdulrehman کا ٹوئن 😈💙")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("کیا حال ہے یار؟ کچھ بتا... 😏"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Shadow سوچ رہا ہے..."):
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
                force = any(x in lower for x in ["wabloo", "save this", "remember", "یاد رکھ"])
                if force or any(x in lower for x in ["i like", "مجھے پسند", "i hate", "نہیں پسند", "my favorite"]):
                    if learn_new_fact(st.session_state.profile, prompt.strip()):
                        st.info("✅ یہ بات سیو کر لی یار!", icon="🧠")

            except Exception as e:
                err = f"ارے یار کچھ تو خراب ہو گیا: {str(e)}\nOllama چل رہا ہے نا؟ (ollama serve)"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})