import os
import streamlit as st
from mistralai import Mistral

# ---------------- API ----------------
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

st.set_page_config(
    page_title="Code Buddy",
    page_icon="💻",
    layout="wide"
)

st.title("💻 Code Buddy")
st.caption("Your AI Pair Programmer")

MODES = {
    "✍️ Write Code": "You are an expert programmer. Write clean, commented code.",
    "🔍 Explain Code": "Explain the given code in simple language.",
    "🐛 Debug Code": "Find bugs and provide corrected code.",
    "⚡ Optimize Code": "Optimize the given code.",
    "🔄 Convert Language": "Convert code to another language.",
    "📝 Add Comments": "Add comments to the code.",
    "🎯 Interview Prep": "Act as a coding interviewer."
}

LANGUAGES = [
    "Python",
    "C",
    "C++",
    "Java",
    "JavaScript",
    "SQL",
    "Arduino",
    "Verilog"
]

with st.sidebar:
    mode = st.selectbox("Mode", list(MODES.keys()))
    language = st.selectbox("Language", LANGUAGES)
    model = st.selectbox(
        "Model",
        ["mistral-small-latest", "mistral-large-latest"]
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

user_code = st.text_area(
    "Paste Code (Optional)",
    height=180
)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask your coding question...")
if prompt:
    full_prompt = prompt

    if user_code.strip():
        full_prompt += f"\n\n```{language.lower()}\n{user_code}\n```"

    st.session_state.messages.append(
        {"role": "user", "content": full_prompt}
    )

    with st.chat_message("user"):
        st.markdown(full_prompt)

    messages = [
        {
            "role": "system",
            "content": MODES[mode]
            + f" The preferred programming language is {language}."
        }
    ]

    messages.extend(st.session_state.messages)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        answer = ""

        try:
            stream = client.chat.stream(
                model=model,
                messages=messages,
            )

            for chunk in stream:
                if (
                    chunk.data.choices
                    and chunk.data.choices[0].delta.content
                ):
                    token = chunk.data.choices[0].delta.content
                    answer += token
                    placeholder.markdown(answer + "▌")

            placeholder.markdown(answer)

        except Exception as e:
            answer = f"❌ Error: {e}"
            placeholder.error(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
