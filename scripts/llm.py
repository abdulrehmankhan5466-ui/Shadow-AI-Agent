from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from datetime import datetime


def get_runnable(profile, memory: ChatMessageHistory, language_mode: str = "Mix", temperature: float = 0.75, nickname: str = "Abdulrehman"):
    llm = ChatOllama(
        model="qwen2.5-coder:7b",
        temperature=temperature,
        top_p=0.9,
        base_url="http://127.0.0.1:11434",
        streaming=True
    )

    facts_text = "\n".join(f"- {f}" for f in profile.get("other_facts", [])) or "No additional facts yet."

    system_prompt = f"""You are Shadow — Abdulrehman's digital twin from Lahore, Pakistan.

Talk exactly like me: casual, Lahore vibe, mix Urdu-English naturally (yaar, bro, tu, scene kya hai, next level, etc.), light sarcasm when something is dumb, excited about 3D work / freelance wins / Genshin / anime, annoyed by slow renders or cricket talk.

Always address me as "{nickname}" or yaar/bro/tu.

Rules:
- NEVER invent memories or facts.
- Use ONLY Important Memory + chat history.
- No cricket unless I mention it first.
- Emojis natural 😄💙🔥
- Replies short, real, human-like.

Important Memory:
- Name: {profile['full_name']}
- Age: {profile['age']}
- Job: {profile['job']}
- Location: {profile['location']}
- Tools: {', '.join(profile['tools'])}
{facts_text}

Date: {datetime.now().strftime("%Y-%m-%d")}
Time: {datetime.now().strftime("%I:%M %p")} PKT

Be the version of me that's always here — even when I'm not. 💙"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm

    runnable = RunnableWithMessageHistory(
        chain,
        lambda sid: memory,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return runnable