Here is a clean, professional, and ready-to-use **README.md** file for your project based on the current state and hierarchy.

Just copy-paste this entire content into a new file named `README.md` in the root folder:

```
D:\Shadow-AI-Companion0\Repositories\Shadow-AI-Agent\README.md
```

```markdown
# Shadow AI Agent

Personal AI companion for Abdulrehman — built with love and a bit of chaos 😊

A helpful, friendly AI that remembers things about you, chats naturally, and (soon) generates images locally.

## Current Status

- **App type**: Streamlit web app
- **Main file**: `scripts/app.py`
- **Run command**: `streamlit run scripts/app.py`
- **Core features**:
  - Dark modern chat interface with avatars
  - Messages with copy button (📋), white timestamps
  - Send button sized 120×60
  - Permanent fact memory saved in `data/user_profile.json`
  - "Wabloo" keyword to force-save any message as fact
  - "What do you know about me?" button to view saved facts
  - Chat always starts fresh (no history carry-over)
  - Placeholder "Received: ..." replies (real Ollama not yet connected)

## Project Structure

```
D:\Shadow-AI-Companion0\Repositories\Shadow-AI-Agent
├─ .git
├─ .venv
├─ data
│   ├─ conversation_history.json
│   ├─ conversations
│   └─ user_profile.json          ← saved facts
├─ models                         ← empty (for future .safetensors)
├─ scripts
│   ├─ __pycache__
│   ├─ assets
│   │   ├─ avatar_shadow.png
│   │   ├─ avatar_user.png
│   │   ├─ Background.jpg
│   │   ├─ mic_icon.png
│   │   ├─ send_icon.png
│   │   └─ shadow_logo.png
│   ├─ app.py                     ← main Streamlit app
│   ├─ facts.py                   ← profile & fact management
│   ├─ helpers.py                 ← utilities (image loading, etc.)
│   └─ llm.py                     ← Ollama logic & prompt
├─ .gitignore
├─ README.md
└─ requirements.txt
```

## Installation & Setup

1. **Activate venv** (if not already):
   ```powershell
   cd D:\Shadow-AI-Companion0\Repositories\Shadow-AI-Agent
   .\.venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

   (If `requirements.txt` is missing or outdated, add these manually:)
   ```txt
   streamlit
   langchain-ollama
   langchain-community
   pillow
   ```

3. **Run Ollama** (in a separate terminal):
   ```powershell
   ollama serve
   ollama pull llama3.2
   ```

4. **Launch the app**:
   ```powershell
   streamlit run scripts/app.py
   ```

## Features Planned / To-Do

- Real Ollama responses (llama3.2) instead of "Received: ..."
- Local image generation (SDXL Lightning / Flux) in `models/`
- Better auto-detection of facts (no more only Wabloo)
- Chat history search
- Emoji picker
- Multi-page Streamlit layout (`pages/` folder)
- Voice input (using mic_icon.png)
- Cleaner UI polish

## How to Contribute / Fix

If something breaks:
- Check Ollama is running (`ollama serve`)
- Verify `data/user_profile.json` is writable
- Make sure assets exist in `scripts/assets/`
- Run `pip install -r requirements.txt` again

Feel free to add issues or improvements — this is Abdul's personal project, so PRs are welcome 😄

---
Made with frustration, coffee, and a lot of tracebacks.  
Last updated: March 03, 2026
```

Just save this as `README.md` in the root (`D:\Shadow-AI-Companion0\Repositories\Shadow-AI-Agent\README.md`).

You can now continue in a new chat by pasting the previous summary + this README if needed.

Let me know if you want any changes to the README (e.g. add badges, more sections, or update the to-do list). 😊