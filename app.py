import streamlit as st
from cache.semantic_cache import wrapper

st.set_page_config(page_title="Semantic Cache Demo", page_icon="🧠", layout="wide")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


st.title("College Helpdesk — Semantic Cache Demo")

st.sidebar.header("📊 Stats")

if st.sidebar.button("Reset Session"):
    st.session_state.chat_history = []
    st.rerun()

total_query = len(st.session_state.chat_history)
hit_count = sum(1 for d in st.session_state.chat_history if d["source"] == "HIT")
hit_rate = hit_count/total_query if total_query > 0 else 0
total_tokens_used = sum(d["tokens"] for d in st.session_state.chat_history if d["source"] == "MISS")

st.sidebar.metric("Total Query", total_query)
st.sidebar.metric("HIT Count", hit_count)
st.sidebar.metric("HIT Rate", f"{hit_rate*100:.1f}%")
st.sidebar.progress(hit_rate)
st.sidebar.metric("Tokens Used (MISS only)", total_tokens_used)


query = st.chat_input("Write a message...")

if query:
    try:
        with st.spinner("Answer Loading"):
            query_reply = wrapper(query)
        st.session_state.chat_history.append({
            "query": query,
            "answer": query_reply["answer"],
            "source": query_reply["source"],
            "latency": query_reply["latency"],
            "tokens": query_reply["tokens"]
        })
    except Exception as e:
        st.error("Any Problem 'Please Try Again'")

if len(st.session_state.chat_history) == 0:
    st.info("Ask only college related query — Example 'how much is the hostel fee'")

for dictionary in st.session_state.chat_history[::-1]:
    with st.chat_message("user"):
        st.write(dictionary["query"])
    with st.chat_message("assistant"):
        st.write(dictionary["answer"])
        if dictionary["source"] == "HIT":
            st.caption(f"⚡ Cache HIT — instant ({dictionary['latency']}s)")
        else:
            st.caption(f"🤖 LLM MISS — {dictionary['latency']:.2f}s, {dictionary['tokens']} tokens")



