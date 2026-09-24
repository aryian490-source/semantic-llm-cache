import time
import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

load_dotenv()
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.environ.get("GROQ_API_KEY")
def mock_llm(query):
    start_time = time.time()
    client = Groq(
    api_key=api_key
    )

    chat_completion = client.chat.completions.create(
    messages=[
    {
    "role": "system",
    "content": "You are a college helpdesk assistant. Only answer college-related queries. If the query is unrelated, reply: Sorry, I don't know about this."
    },
    {
    "role": "user",
    "content": query
    }
    ],
    model="openai/gpt-oss-20b",
    )
    end_time = time.time()
    latency = end_time - start_time
    answer = chat_completion.choices[0].message.content
    tokens = chat_completion.usage.total_tokens
    return {"answer": answer , "tokens": tokens , "latency": latency}

