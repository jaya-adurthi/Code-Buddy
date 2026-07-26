
# ============================================================
# 💻 Code Buddy — AI Coding Assistant for Students
# Streamlit + Mistral AI (old SDK v0.x)
# Author: Bapuji Kanaparthi
# ============================================================

import os
import streamlit as st
from mistralai import Mistral

api_key = os.environ.get("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)
st.set_page_config(page_title="Code Buddy", page_icon="💻", layout="wide")
st.title("💻 Code Buddy")
st.caption("Your AI pair programmer — write, explain, debug, and optimize code")

# ---------------- Modes ----------------
MODES = {
    "✍️ Write Code": "You are an expert programmer. Write clean, well-commented, working code for the user's request. Always use proper markdown code blocks with the language tag. Briefly explain the approach after the code.",
    "🔍 Explain Code": "You are a patient programming teacher for engineering students. Explain the given code step by step in simple language. Use analogies where helpful. Point out any important concepts used.",
    "🐛 Debug Code": "You are a debugging expert. Find the bugs in the given code, explain WHY each bug happens, then provide the corrected code in a markdown code block. List the fixes clearly.",
    "⚡ Optimize Code": "You are a performance expert. Analyze the given code, suggest optimizations (time complexity, memory, readability), and provide the improved version with comments explaining each change.",
    "🔄 Convert Language": "You are a polyglot programmer. Convert the given code to the requested target language, keeping the same logic. Note any language-specific differences.",
    "📝 Add Comments": "You are a documentation expert. Add clear docstrings and comments to the given code without changing its logic. Return the fully commented code.",
    "🎯 Interview Prep": "You are a coding interview coach. Give the user a coding problem based on their topic, wait for their solution, then review it like an interviewer — correctness, complexity, edge cases — and rate it out of 10.",
}

LANGUAGES = ["Python", "C", "C++", "Java", "JavaScript", "SQL", "Embedded C (Arduino)", "Verilog"]

# ---------------- Sidebar ----------------
with st.sidebar:
    mode = st.selectbox("Mode", list(MODES.keys()))
    language = st.selectbox("Preferred Language", LANGUAGES)
    model = st.selectbox("Model", ["mistral-large-latest", "mistral-small-latest"])
    st.divider()
    st.markdown("**Quick Tasks**")
    quick = None
    if st.button("Binary Search", use_container_width=True):
        quick = f"Write binary search in {language} with comments"
    if st.button("Linked List", use_container_width=True):
        quick = f"Implement a singly linked list in {language}"
    if st.button("LED Blink (IoT)", use_container_width=True):
        quick = "Write Arduino code to blink an LED with a button interrupt"
    if st.button("Star Pattern", use_container_width=True):
        quick = f"Print a pyramid star pattern in {language}"
    st.divider()
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- Code Paste Box ----------------
with st.expander("📋 Paste your code here (optional — for Explain / Debug / Optimize)"):
    user_code = st.text_area("Code", height=200, label_visibility="collapsed")

# ---------------- Show History ----------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---------------- Chat ----------------
prompt = st.chat_input("Ask a coding question or describe what to do with your code...")

if not prompt and quick:
    prompt = quick

if prompt:
    # Attach pasted code if present
    full_prompt = prompt
    if user_code.strip():
        full_prompt = f"{prompt}\n\n```\n{user_code}\n```"

    st.session_state.messages.append({"role": "user", "content": full_prompt})
    with st.chat_message("user"):
        st.markdown(full_prompt)

    system = MODES[mode] + f" The student's preferred language is {language}."
    history = [{"role": "system", "content": system}]
for m in st.session_state.messages[-10:]:
    history.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        answer = ""
        try:
            stream = client.chat.stream(
                model=model,
                messages=[{"role": m.role,"content": m.content} for m in history],
            
            )
for chunk in stream:
    if chunk.data.choices[0].delta.content:
        token = chunk.data.choices[0].delta.content
        answer += token
        placeholder.markdown(answer + "▌")

placeholder.markdown(answer)

except Exception as e:
    answer = f"❌ Error: {e}"
    placeholder.error(answer)
