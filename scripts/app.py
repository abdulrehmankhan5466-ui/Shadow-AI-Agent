import streamlit as st
from datetime import datetime
import time
from pathlib import Path
import json

from facts import load_profile, learn_new_fact, PROFILE_FILE
from llm import get_runnable
from langchain_community.chat_message_histories import ChatMessageHistory

# Image generation (add your model path below)
try:
    from diffusers import DiffusionPipeline
    import torch
except ImportError:
    DiffusionPipeline = None
    torch = None

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
    st.session_state.temperature = 0.75

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True

if "nickname" not in st.session_state:
    st.session_state.nickname = "Abdulrehman"

# Re-create runnable when settings change
if ("runnable" not in st.session_state or
    st.session_state.get("last_lang") != st.session_state.language_mode or
    st.session_state.get("last_temp") != st.session_state.temperature or
    st.session_state.get("last_memory") != st.session_state.memory_enabled or
    st.session_state.get("last_nickname") != st.session_state.nickname):

    st.session_state.runnable = get_runnable(
        st.session_state.profile,
        st.session_state.memory if st.session_state.memory_enabled else ChatMessageHistory(),
        st.session_state.language_mode,
        st.session_state.temperature,
        st.session_state.nickname
    )
    st.session_state.last_lang = st.session_state.language_mode
    st.session_state.last_temp = st.session_state.temperature
    st.session_state.last_memory = st.session_state.memory_enabled
    st.session_state.last_nickname = st.session_state.nickname

# Image pipe (cached)
@st.cache_resource
def load_image_pipe():
    if DiffusionPipeline is None:
        return None
    # CHANGE THIS PATH TO YOUR MODEL FILE
    model_path = r"D:\Shadow-AI-Companion0\Repositries\Shadow-AI-Agent\models\flux1-schnell.safetensors"  # ← edit here
    pipe = DiffusionPipeline.from_single_file(
        model_path,
        torch_dtype=torch.float16,
        use_safetensors=True
    )
    pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    pipe.enable_model_cpu_offload()
    return pipe

image_pipe = load_image_pipe()

# ────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────

st.sidebar.title("Shadow 💙")
st.sidebar.markdown("Abdulrehman's Shadow")

st.sidebar.caption(f"Loaded facts: {len(st.session_state.profile.get('other_facts', []))}")

# Nickname selector
nickname_options = ["Abdulrehman", "Maan", "Remi", "Ronnie", "Sharlon", "Random"]
st.sidebar.selectbox(
    "Call me",
    options=nickname_options,
    index=nickname_options.index(st.session_state.nickname),
    key="nickname_select"
)
st.session_state.nickname = st.session_state.nickname_select

# Memory toggle
st.sidebar.toggle(
    "Use conversation memory",
    value=st.session_state.memory_enabled,
    key="memory_toggle"
)
st.session_state.memory_enabled = st.session_state.memory_toggle

# Language
st.sidebar.radio(
    "Reply language",
    options=["English", "Urdu", "Mix"],
    index=["English", "Urdu", "Mix"].index(st.session_state.language_mode),
    key="lang_radio"
)
st.session_state.language_mode = st.session_state.lang_radio

# Temperature
st.sidebar.slider(
    "Creativity (temperature)",
    0.6, 1.2, st.session_state.temperature, 0.05,
    key="temp_slider"
)
st.session_state.temperature = st.session_state.temp_slider

if st.sidebar.button("New Chat"):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("Clear All"):
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
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != msg:
        st.session_state.messages.append({"role": "assistant", "content": msg})
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(f"Profile: {PROFILE_FILE}")

# ────────────────────────────────────────────────
# Main chat
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

            # Image generation trigger
            if any(word in prompt.lower() for word in ["generate image", "make image", "create image", "show me as", "generate me"]):
                img_prompt = prompt.lower().replace("generate image of", "").replace("make image of", "").replace("create image of", "").strip()
                if img_prompt and image_pipe:
                    with st.spinner("Generating image... ~10–40 sec"):
                        try:
                            image = image_pipe(
                                prompt=img_prompt + ", high detail, cinematic lighting",
                                num_inference_steps=6,
                                guidance_scale=0.0
                            ).images[0]
                            st.image(image, caption=f"Generated: {img_prompt}", use_column_width=True)

                            save_dir = Path("data/generated")
                            save_dir.mkdir(exist_ok=True)
                            save_path = save_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                            image.save(save_path)
                            st.success(f"Saved → {save_path}")
                        except Exception as e:
                            st.error(f"Image failed: {str(e)}")

            # Blender script helper
            if "blender script" in prompt.lower() or "script for blender" in prompt.lower():
                st.markdown("**Blender Python script:**")
                st.code(full_response, language="python")
                st.info("1. Open Blender\n2. Scripting workspace\n3. New text block\n4. Paste & Run")

            # Fact learning
            lower = prompt.lower()
            force = any(x in lower for x in ["wabloo", "save this", "remember that"])
            if force or any(x in lower for x in ["i like", "مجھے پسند", "i hate", "نہیں پسند", "my favorite"]):
                if learn_new_fact(st.session_state.profile, prompt.strip()):
                    st.info("✅ Saved as fact!", icon="🧠")
                    st.rerun()

        except Exception as e:
            err = f"Something broke: {str(e)}\nMake sure Ollama is running"
            st.error(err)
            st.session_state.messages.append({"role": "assistant", "content": err})