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
    st.session_state.language_mode = "Mix"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.85

# Re-create runnable only when needed
if ("runnable" not in st.session_state or
    "last_lang" not in st.session_state or
    "last_temp" not in st.session_state or
    st.session_state.last_lang != st.session_state.language_mode or
    st.session_state.last_temp != st.session_state.temperature):

    st.session_state.runnable = get_runnable(
        st.session_state.profile,
        st.session_state.memory,
        st.session_state.language_mode,
        st.session_state.temperature
    )
    st.session_state.last_lang = st.session_state.language_mode
    st.session_state.last_temp = st.session_state.temperature

# ────────────────────────────────────────────────
# Helpers for language-aware text
# ────────────────────────────────────────────────

def txt(en, ur):
    if st.session_state.language_mode == "Urdu":
        return ur
    elif st.session_state.language_mode == "English":
        return en
    else:
        return f"{en} / {ur}" if en and ur else (en or ur)

# ────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────

st.sidebar.title(txt("Shadow", "شیڈو") + " 💙")
st.sidebar.markdown(txt("Abdulrehman's digital twin", "عبدالرحمان کا ڈیجیٹل ٹوئن"))

# Language selector
st.sidebar.subheader(txt("Language", "زبان"))

lang_options = ["English", "Urdu", "Mix"]
lang_display = {
    "English": txt("English", "انگریزی"),
    "Urdu": txt("Urdu", "اردو"),
    "Mix": txt("Mix (Urdu + English)", "مکس (اردو + انگریزی)")
}

selected_display = st.sidebar.radio(
    txt("Reply language", "جواب کی زبان"),
    options=[lang_display[k] for k in lang_options],
    index=lang_options.index(st.session_state.language_mode)
)

# Map back to internal key
for k, v in lang_display.items():
    if v == selected_display:
        st.session_state.language_mode = k
        break

# Temperature
st.sidebar.subheader(txt("Creativity", "تخلیقی صلاحیت"))
st.session_state.temperature = st.sidebar.slider(
    txt("Temperature", "درجہ حرارت"),
    0.6, 1.2, st.session_state.temperature, 0.05,
    help=txt("Lower = more focused\nHigher = more creative", "کم = زیادہ سنجیدہ\nزیادہ = زیادہ تخلیقی")
)

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button(txt("New Chat", "نیا چیٹ"), use_container_width=True):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button(txt("Clear All", "سب صاف"), use_container_width=True):
        st.session_state.messages = []
        st.session_state.memory.clear()
        st.rerun()

if st.sidebar.button(txt("What I know about you", "تیرے بارے میں کیا جانتا ہوں")):
    facts = st.session_state.profile.get("other_facts", [])
    if facts:
        facts_md = "\n".join(f"- {f}" for f in facts)
        msg = txt("**What I remember:**", "**جو یاد ہے:**") + f"\n\n{facts_md}"
    else:
        msg = txt("Nothing special saved yet — tell me more!", "ابھی کچھ خاص سیو نہیں — کچھ بتا یار!")
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Profile → data/user_profile.json")

# ────────────────────────────────────────────────
# Main area
# ────────────────────────────────────────────────

st.title(txt("Shadow – Your Digital Twin", "شیڈو – تیرا ڈیجیٹل ٹوئن") + " 💙")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(txt("What's on your mind?", "کیا سوچ رہا ہے یار؟")):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(txt("Shadow is thinking...", "شیڈو سوچ رہا ہے...")):
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
                    time.sleep(0.01)

                message_placeholder.markdown(full_response)

                st.session_state.messages.append({"role": "assistant", "content": full_response})

                # Fact learning
                lower = prompt.lower()
                force = any(x in lower for x in ["wabloo", "save this", "remember", "یاد رکھ"])
                if force or any(x in lower for x in ["i like", "مجھے پسند", "i hate", "نہیں پسند", "my favorite"]):
                    if learn_new_fact(st.session_state.profile, prompt.strip()):
                        st.info(txt("✅ Saved as fact!", "✅ یہ بات سیو ہو گئی!"), icon="🧠")

            except Exception as e:
                err = txt(
                    f"Oops — something broke: {str(e)}\nIs Ollama running? (ollama serve)",
                    f"یار کچھ خراب ہو گیا: {str(e)}\nاولاما چل رہا ہے نا؟ (ollama serve)"
                )
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})