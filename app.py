
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="GhimireyGPT",
    page_icon="G",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
except Exception:
    API_KEY = os.getenv("OPENROUTER_API_KEY", "")

MODEL = "openrouter/free"

# ---------------- SESSION DATA ----------------

if "chats" not in st.session_state:
    st.session_state.chats = {"New chat": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New chat"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# ---------------- DESIGN ----------------

st.markdown("""
<style>

/* Global */
.stApp {
    background: #212121;
    color: #ececec;
}

header, footer, #MainMenu, .stDeployButton {
    visibility: hidden;
}

.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 8rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #171717;
    border-right: 1px solid #303030;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.3rem 1rem;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #eeeeee;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton button {
    background: transparent;
    border: none;
    color: #eeeeee;
    border-radius: 9px;
    text-align: left;
    padding: 10px 12px;
    font-size: 14px;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: #292929;
}

/* Hide chat avatars completely */
[data-testid="stChatMessageAvatar"] {
    display: none !important;
}

/* Remove default chat cards */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 16px 0 !important;
    gap: 0 !important;
}

/* Chat content */
[data-testid="stChatMessageContent"] {
    color: #ececec !important;
    line-height: 1.75;
    font-size: 16px;
}

/* User message */
[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageContent"]
) {
    border-radius: 12px;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: #303030 !important;
    border: 1px solid #454545 !important;
    border-radius: 25px !important;
    padding: 5px 10px !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 15px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #999999 !important;
}

/* Send button */
[data-testid="stChatInput"] button {
    background: #eeeeee !important;
    color: #171717 !important;
    border-radius: 50% !important;
}

/* Welcome */
.welcome {
    text-align: center;
    margin-top: 25vh;
}

.welcome h1 {
    font-size: 32px;
    font-weight: 600;
    color: #eeeeee;
    letter-spacing: -1px;
}

.welcome p {
    color: #999999;
    font-size: 14px;
}

/* Small heading */
.brand {
    font-size: 19px;
    font-weight: 650;
    letter-spacing: -0.5px;
    color: #eeeeee;
    padding: 5px 0 18px 5px;
}

/* Sidebar label */
.history-label {
    font-size: 12px;
    color: #888888;
    padding: 20px 8px 8px;
}

/* Footer */
.note {
    text-align: center;
    color: #777777;
    font-size: 11px;
    padding-top: 10px;
}

/* Mobile */
@media(max-width: 768px) {
    .block-container {
        padding: 1rem 1rem 7rem;
    }

    .welcome {
        margin-top: 22vh;
    }

    .welcome h1 {
        font-size: 25px;
    }
}

</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown(
        '<div class="brand">GhimireyGPT</div>',
        unsafe_allow_html=True
    )

    if st.button("+  New chat", use_container_width=True):
        st.session_state.chat_counter += 1
        name = f"New chat {st.session_state.chat_counter}"
        st.session_state.chats[name] = []
        st.session_state.current_chat = name
        st.rerun()

    st.markdown(
        '<div class="history-label">Your chats</div>',
        unsafe_allow_html=True
    )

    for name in reversed(list(st.session_state.chats.keys())):
        if st.button(
            name,
            key="history_" + name,
            use_container_width=True
        ):
            st.session_state.current_chat = name
            st.rerun()


# ---------------- CHAT DATA ----------------

messages = st.session_state.chats[
    st.session_state.current_chat
]


# ---------------- WELCOME SCREEN ----------------

if not messages:

    st.markdown("""
    <div class="welcome">
        <h1>What's on your mind?</h1>
        <p>Ask anything. Let's figure it out together.</p>
    </div>
    """, unsafe_allow_html=True)


# ---------------- SHOW MESSAGES ----------------

for msg in messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------- MESSAGE INPUT ----------------

prompt = st.chat_input("How's your day going?")

if prompt:
    st.session_state.pending_prompt = prompt

# Process a new message
if st.session_state.pending_prompt:

    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    messages = st.session_state.chats[
        st.session_state.current_chat
    ]

    messages.append({
        "role": "user",
        "content": prompt
    })

    # Automatically name the conversation
    if len(messages) == 1:
        old_name = st.session_state.current_chat
        new_name = prompt[:30].strip()

        if not new_name:
            new_name = "New conversation"

        if new_name in st.session_state.chats:
            st.session_state.chat_counter += 1
            new_name = f"{new_name} ({st.session_state.chat_counter})"

        st.session_state.chats[new_name] = messages
        del st.session_state.chats[old_name]
        st.session_state.current_chat = new_name

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):

        if not API_KEY:
            st.error("API key missing. Check your Streamlit Secrets.")

        else:
            try:
                llm = ChatOpenAI(
                    model=MODEL,
                    api_key=API_KEY,
                    base_url="https://openrouter.ai/api/v1",
                    temperature=0.7
                )

                conversation = [
                    SystemMessage(
                        content=(
                            "You are a helpful, intelligent and natural AI assistant. "
                            "Talk like a thoughtful human conversational partner. "
                            "Avoid robotic language, unnecessary headings and generic "
                            "introductions. Be clear, direct and conversational."
                        )
                    )
                ]

                for msg in messages:
                    if msg["role"] == "user":
                        conversation.append(
                            HumanMessage(content=msg["content"])
                        )
                    else:
                        conversation.append(
                            AIMessage(content=msg["content"])
                        )

                with st.spinner(""):
                    response = llm.invoke(conversation)

                answer = response.content

                if isinstance(answer, list):
                    answer = "\n".join(
                        str(item.get("text", item))
                        if isinstance(item, dict)
                        else str(item)
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


# ---------------- BOTTOM WATERMARK ----------------

st.markdown(
    '<div class="note">GhimireyGPT can make mistakes. Check important information.</div>',
    unsafe_allow_html=True
)
