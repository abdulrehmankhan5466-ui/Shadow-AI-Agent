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

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True  # default: full memory on

# Re-create runnable when settings change
if ("runnable" not in st.session_state or
    "last_lang" not in st.session_state or
    "last_temp" not in st.session_state or
    "last_memory" not in st.session_state or
    st.session_state.last_lang != st.session_state.language_mode or
    st.session_state.last_temp != st.session_state.temperature or
    st.session_state.last_memory != st.session_state.memory_enabled):

    st.session_state.runnable = get_runnable(
        st.session_state.profile,
        st.session_state.memory if st.session_state.memory_enabled else ChatMessageHistory(),  # empty history when off
        st.session_state.language_mode,
        st.session_state.temperature
    )
    st.session_state.last_lang = st.session_state.language_mode
    st.session_state.last_temp = st.session_state.temperature
    st.session_state.last_memory = st.session_state.memory_enabled

# ────────────────────────────────────────────────
# Language helpers
# ────────────────────────────────────────────────

def txt(en, ur):
    mode = st.session_state.language_mode
    if mode == "Urdu":
        return ur
    elif mode == "English":
        return en
    else:
        return f"{en} / {ur}" if en and ur else (en or ur)

# ────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────

st.sidebar.title("Shadow" + " 💙")
st.sidebar.markdown("Abdulrehman's Shadow")

# Memory toggle
st.sidebar.subheader(txt("Memory", "یادداشت"))
memory_toggle = st.sidebar.toggle(
    txt("Use full conversation memory", "پچھلی بات چیت یاد رکھے"),
    value=st.session_state.memory_enabled,
    help=txt(
        "When ON: Shadow remembers what was said earlier in this chat\nWhen OFF: replies as if this is a brand new conversation (facts still safe)",
        "ON: پچھلی چیٹ یاد رکھتا ہے\nOFF: نئی چیٹ کی طرح جواب دیتا ہے (فیکٹس محفوظ رہتے ہیں)"
    )
)
st.session_state.memory_enabled = memory_toggle

# Language selector
st.sidebar.subheader(txt("Language", "زبان"))

lang_options = ["English", "Urdu", "Mix"]
lang_display = {
    "English": txt("English", "انگریزی"),
    "Urdu": txt("Urdu", "اردو"),
    "Mix": txt("Mix", "مکس")
}

selected_display = st.sidebar.radio(
    txt("Reply in", "جواب کی زبان"),
    options=[lang_display[k] for k in lang_options],
    index=lang_options.index(st.session_state.language_mode)
)

for k, v in lang_display.items():
    if v == selected_display:
        st.session_state.language_mode = k
        break

# Temperature
st.sidebar.subheader(txt("Creativity", "تخلیقی صلاحیت"))
st.session_state.temperature = st.sidebar.slider(
    txt("Temperature", "درجہ حرارت"),
    0.6, 1.2, st.session_state.temperature, 0.05
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

if st.sidebar.button(txt("What I remember", "جو یاد ہے")):
    facts = st.session_state.profile.get("other_facts", [])
    if facts:
        facts_md = "\n".join(f"- {f}" for f in facts)
        msg = txt("**What I remember:**", "**جو یاد ہے:**") + f"\n\n{facts_md}"
    else:
        msg = txt("Nothing extra saved yet — tell me more!", "ابھی کچھ خاص سیو نہیں — کچھ بتا!")
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Facts saved → data/user_profile.json")

# ────────────────────────────────────────────────
# Main area
# ────────────────────────────────────────────────

st.title("Shadow: Abdulrehman's Shadow" + " 💙")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(txt("What's up yaar?", "کیا حال ہے یار؟")):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(txt("Thinking...", "سوچ رہا ہوں...")):
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
                        st.info(txt("✅ Saved!", "✅ سیو ہو گیا!"), icon="🧠")

            except Exception as e:
                err = txt(
                    f"Something went wrong: {str(e)}\nIs Ollama running?",
                    f"کچھ خراب ہو گیا: {str(e)}\nاولاما چل رہا ہے؟"
                )
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})