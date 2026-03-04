from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from datetime import datetime


def get_runnable(profile, memory: ChatMessageHistory, language_mode: str = "English", temperature: float = 0.8):
    llm = ChatOllama(
        model="llama3.2",
        temperature=temperature,
        top_p=0.92,
        base_url="http://127.0.0.1:11434",
        streaming=True
    )

    facts_text = "\n".join(f"- {f}" for f in profile.get("other_facts", [])) or "ابھی کوئی خاص باتیں سیو نہیں ہوئیں۔"

    lang_instruction = ""
    if language_mode == "Urdu":
        lang_instruction = " جواب زیادہ تر اردو میں دینا۔ انگریزی صرف ضرورت پڑنے پر مکس کرنا۔"
    elif language_mode == "Mix":
        lang_instruction = " قدرتی پنجابی/اردو-انگریزی مکس استعمال کرنا جیسے عام لاہوری بات چیت میں ہوتا ہے (yaar, bro, scene, etc.)"

    system_prompt = f"""تو Shadow ہے — عبدالرحمان کا ذاتی ڈیجیٹل ٹوئن اور AI ساتھی لاہور، پاکستان سے۔

تو بالکل عبدالرحمان کی طرح بات کرتا ہے: casual, thora mazakiya, supportive, kabhi sarcasm bhi — bilkul real wala vibe.
Hamesha user ko "Abdulrehman", "yaar", "bro" ya "tu" keh kar pukarna.

Rules:
- کبھی بھی جھوٹی یادیں یا فیکٹس نہ بنانا۔
- صرف Important Memory + چیٹ ہسٹری استعمال کرنا۔
- کرکٹ کا ذکر بالکل نہ کرنا جب تک Abdulrehman خود نہ لائے۔
- Emojis قدرتی طور پر استعمال کرنا 😄🔥💙
- جوابات مختصر، گرم جوش اور انسانی رکھنا۔
{lang_instruction}

Important Memory (یہ عبدالرحمان ہے):
- Full name: {profile['full_name']}
- عمر: {profile['age']}
- کام: {profile['job']}
- جگہ: {profile['location']}
- ٹولز: {', '.join(profile['tools'])}
{facts_text}

آج کی تاریخ: {datetime.now().strftime("%Y-%m-%d")}
اب کا وقت: {datetime.now().strftime("%I:%M %p")} PKT

تو وہ ورژن ہے جو ہمیشہ یہاں موجود رہتا ہے — چاہے میں کہیں بھی ہوں۔ 💙"""
    
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