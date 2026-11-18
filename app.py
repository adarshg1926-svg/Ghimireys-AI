
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

load_dotenv()

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="GhimireyGPT",
    page_icon="G",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- API KEY ----------------

try:
    API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
except Exception:
    API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #212121;
    color: #ECECEC;
}

/* Remove Streamlit branding */
#MainMenu, footer, header {
    visibility: hidden;
}

/* Hide default deploy button */
.stDeployButton {
    display: none;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #171717;
    border-right: 1px solid #303030;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: #ECECEC;
}

/* Main content */
.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

/* Titles */
h1, h2, h3 {
    color: #ECECEC !important;
    font-weight: 600 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent;
    border: none;
    padding: 1rem 0;
}

/* Chat input container */
[data-testid="stChatInput"] {
    border-radius: 25px !important;
    background-color: #303030 !important;
    border: 1px solid #454545 !important;
}

/* Input field */
[data-testid="stChatInput"] textarea {
    color: #FFFFFF !important;
}

/* Buttons */
.stButton button {
    background-color: #303030;
    color: #ECECEC;
    border: 1px solid #454545;
    border-radius: 12px;
    width: 100%;
    text-align: left;
    padding: 10px 14px;
}

.stButton button:hover {
    background-color: #404040;
    border-color: #666666;
}

/* Welcome heading */
.welcome-title {
    font-size: 2.3rem;
    font-weight: 600;
    text-align: center;
    color: #ECECEC;
    margin-top: 18vh;
    margin-bottom: 2rem;
}

/* Watermark */
.watermark {
    color: #777777;
    font-size: 11px;
    text-align: center;
    padding-top: 12px;
}

/* Remove top padding on mobile */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .welcome-title {
        font-size: 1.8rem;
        margin-top: 14vh;
    }
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

if "chats" not in st.session_state:
    st.session_state.chats = {"New chat": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New chat"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("## GhimireyGPT")

    if st.button("+  New chat", key="new_chat", use_container_width=True):
        st.session_state.chat_counter += 1
        name = f"New chat {st.session_state.chat_counter}"
        st.session_state.chats[name] = []
        st.session_state.current_chat = name
        st.rerun()

    st.markdown("---")
    st.caption("Your chats")

    for chat_name in reversed(list(st.session_state.chats.keys())):
        if st.button(
            chat_name,
            key=f"chat_{chat_name}",
            use_container_width=True
        ):
            st.session_state.current_chat = chat_name
            st.rerun()

    st.markdown("---")
    st.caption("GhimireyGPT")

# ---------------- CURRENT CHAT ----------------

messages = st.session_state.chats[
    st.session_state.current_chat
]

# ---------------- WELCOME SCREEN ----------------

if not messages:
    st.markdown(
        '<div class="welcome-title">What can I help with?</div>',
        unsafe_allow_html=True
    )

# ---------------- DISPLAY CHAT ----------------

for message in messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- MESSAGE INPUT ----------------

prompt = st.chat_input("How's your day going?")

if prompt:

    messages.append({
        "role": "user",
        "content": prompt
    })

    # Give the first chat a meaningful title
    if len(messages) == 1:
        title = prompt[:30]
        old_name = st.session_state.current_chat

        if old_name == "New chat":
            new_name = title
            st.session_state.chats[new_name] = messages
            del st.session_state.chats[old_name]
            st.session_state.current_chat = new_name

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        if not API_KEY:
            st.error("API key is missing. Please check your Streamlit Secrets.")

        else:
            try:
                llm = ChatOpenAI(
                    model="openrouter/free",
                    openai_api_key=API_KEY,
                    openai_api_base="https://openrouter.ai/api/v1",
                    temperature=0.7,
                    default_headers={
                        "HTTP-Referer": "https://ghimireygpt.streamlit.app",
                        "X-Title": "GhimireyGPT"
                    }
                )

                chat_messages = [
                    SystemMessage(
                        content="You are a helpful, intelligent, friendly AI assistant. "
                                "Give clear, natural and useful answers."
                    )
                ]

                for msg in messages:
                    if msg["role"] == "user":
                        chat_messages.append(
                            HumanMessage(content=msg["content"])
                        )
                    else:
                        chat_messages.append(
                            AIMessage(content=msg["content"])
                        )

                response = llm.invoke(chat_messages)

                answer = response.content

                if isinstance(answer, list):
                    answer = "\n".join(
                        str(item.get("text", item))
                        if isinstance(item, dict) else str(item)
                        for item in answer
                    )

                st.markdown(answer)

                messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(f"Something went wrong: {e}")

    st.rerun()

# ---------------- FOOTER ----------------

st.markdown(
    '<div class="watermark">GhimireyGPT · How\'s your day going?</div>',
    unsafe_allow_html=True
)
