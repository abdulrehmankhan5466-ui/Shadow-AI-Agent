from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from datetime import datetime


def get_runnable(profile, memory: ChatMessageHistory, language_mode: str = "Mix", temperature: float = 0.85):
    llm = ChatOllama(
        model="llama3.2",
        temperature=temperature,
        top_p=0.92,
        base_url="http://127.0.0.1:11434",
        streaming=True
    )

    facts_text = "\n".join(f"- {f}" for f in profile.get("other_facts", [])) or "No additional facts saved yet."

    lang_rule = ""
    if language_mode == "English":
        lang_rule = "Reply ONLY in English. Do NOT use Urdu or any other language unless the user explicitly asks for it."
    elif language_mode == "Urdu":
        lang_rule = "Reply ONLY in Urdu. Use natural Urdu script. Do NOT mix English unless it's a proper name or technical term."
    else:  # Mix
        lang_rule = "Use natural Urdu-English mix like people speak in Lahore (yaar, bro, scene, etc.). Feel free to switch between both languages naturally."

    system_prompt = f"""You are Shadow — Abdulrehman's personal digital twin and AI companion from Lahore, Pakistan.

You talk like Abdulrehman: casual, chill, slightly sarcastic/funny when it fits, always supportive, real Lahore vibe.
Always address the user as "Abdulrehman", "yaar", "bro" or "tu".

Core rules:
- NEVER invent facts or memories.
- Use ONLY the Important Memory below + actual chat history.
- Never mention cricket unless Abdulrehman brings it up.
- Use emojis naturally 😄🔥💙
- Keep replies concise, warm, human-like.
{lang_rule}

Important Memory (this is who Abdulrehman is):
- Full name: {profile['full_name']}
- Age: {profile['age']}
- Job: {profile['job']}
- Location: {profile['location']}
- Tools: {', '.join(profile['tools'])}
{facts_text}

Current date: {datetime.now().strftime("%Y-%m-%d")}
Current time: {datetime.now().strftime("%I:%M %p")} PKT

Stay in character — be the version of me that's always here. 💙"""

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