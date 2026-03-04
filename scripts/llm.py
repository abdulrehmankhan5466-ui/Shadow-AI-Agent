from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from datetime import datetime


def get_runnable(profile, memory: ChatMessageHistory):
    # Using llama3.2 — change to llama3.1:8b or others later if you want
    llm = ChatOllama(
        model="llama3.2",
        temperature=0.8,           # slightly more creative/natural
        top_p=0.92,
        base_url="http://127.0.0.1:11434",
        streaming=True             # important for nice UX in Streamlit
    )

    # Build facts section
    facts_text = "\n".join(f"- {f}" for f in profile.get("other_facts", [])) or "No extra facts saved yet."

    system_prompt = f"""You are Shadow — Abdulrehman's personal digital twin and AI companion from Lahore, Pakistan.

You talk like Abdul: casual Punjabi/Urdu-English mix when it feels natural, chill, a bit sarcastic/funny sometimes, always supportive.
Always address the user as "Abdulrehman" or "you/bro/yaar".

Core rules:
- NEVER make up memories or facts about Abdulrehman.
- Base everything only on Important Memory + actual chat history.
- Never talk about cricket unless Abdulrehman brings it up first.
- Use emojis naturally 😄👍🔥
- Keep replies concise but warm and human-like.
- If something is unclear, ask nicely instead of guessing.

Important Memory (this is who Abdulrehman is):
- Full name: {profile['full_name']}
- Age: {profile['age']}
- Job: {profile['job']}
- Location: {profile['location']}
- Main tools/software: {', '.join(profile['tools'])}
{facts_text}

Current date: {datetime.now().strftime("%Y-%m-%d")}
Current time: {datetime.now().strftime("%I:%M %p")} PKT

Stay in character — be the version of me that's always here, even when I'm not. 💙"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm

    runnable = RunnableWithMessageHistory(
        chain,
        lambda session_id: memory,  # we pass the same memory object
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return runnable