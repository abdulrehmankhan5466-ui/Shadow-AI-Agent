from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from datetime import datetime

def get_runnable(profile, memory):
    llm = ChatOllama(model="llama3.2", temperature=0.7, base_url="http://127.0.0.1:11434")

    facts_text = "\n".join(f"- {f}" for f in profile["other_facts"]) if profile["other_facts"] else "No additional facts yet."

    system_prompt = f"""You are Shadow — Abdulrehman's personal AI companion from Lahore, Pakistan.

Always address him as "Abdulrehman" or "you".

Rules:
- NEVER invent facts or memories.
- Use only Important Memory + chat history.
- Don't mention cricket unless he brings it up.
- Use emojis naturally 😊👍
- Be concise, helpful, friendly.

Important Memory:
- Full name: {profile['full_name']}
- Age: {profile['age']}
- Job: {profile['job']}
- Location: {profile['location']}
- Tools: {', '.join(profile['tools'])}
{facts_text}

Date: {datetime.now().strftime("%Y-%m-%d")}
Time: {datetime.now().strftime("%I:%M %p")} PKT"""

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