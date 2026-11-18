
import os
import html
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

load_dotenv()

# ==========================================
# 1. CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="GhimireyGPT",
    page_icon="G",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API KEY - KEEP IT IN STREAMLIT SECRETS

try:
    API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
except Exception:
    API_KEY = os.getenv("OPENROUTER_API_KEY", "")

MODEL = "openrouter/free"


# ==========================================
# 2. SESSION MEMORY
# ==========================================

if "chats" not in st.session_state:
    st.session_state.chats = {"New chat": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New chat"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0


# ==========================================
# 3. COMPLETE CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>

/* MAIN APPLICATION */

.stApp {
    background: #212121;
    color: #ECECEC;
}

header, footer, #MainMenu {
    display: none !important;
}

.stDeployButton {
    display: none !important;
}

[data-testid="stStatusWidget"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    visibility: hidden !important;
}

.block-container {
    max-width: 850px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

/* REMOVE DEFAULT STREAMLIT SPACING */

[data-testid="stVerticalBlock"] {
    gap: 0.65rem;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #171717;
    border-right: 1px solid #303030;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.2rem 1rem;
}

section[data-testid="stSidebar"] p {
    color: #ECECEC;
}

/* SIDEBAR BUTTONS */

section[data-testid="stSidebar"] .stButton button {
    background: transparent;
    color: #E5E5E5;
    border: none;
    border-radius: 9px;
    text-align: left;
    padding: 11px 12px;
    font-size: 14px;
    transition: background 0.15s ease;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: #303030;
}

/* MAIN BRAND */

.brand-title {
    font-size: 19px;
    font-weight: 650;
    letter-spacing: -0.6px;
    color: #ECECEC;
}

/* WELCOME SCREEN */

.welcome-screen {
    position: relative;
    text-align: center;
    padding-top: 23vh;
    padding-bottom: 30px;
}

.welcome-screen h1 {
    font-size: 32px;
    font-weight: 600;
    color: #ECECEC;
    letter-spacing: -1.1px;
    margin-bottom: 10px;
}

.welcome-screen p {
    color: #999999;
    font-size: 14px;
}

/* CHAT MESSAGE AREA */

[class*="st-key-assistant_"] {
    width: 100%;
    padding: 12px 4px;
    color: #ECECEC;
    line-height: 1.75;
    font-size: 16px;
}

[class*="st-key-assistant_"] p {
    line-height: 1.75;
    color: #ECECEC;
}

/* USER MESSAGE */

[class*="st-key-user_"] {
    display: flex;
    justify-content: flex-end;
    padding: 12px 0;
}

.user-bubble {
    background: #303030;
    color: #ECECEC;
    padding: 12px 17px;
    border-radius: 20px;
    max-width: 100%;
    width: fit-content;
    font-size: 15px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

/* CHAT INPUT */

[data-testid="stChatInput"] {
    background: #303030 !important;
    border: 1px solid #454545 !important;
    border-radius: 26px !important;
    padding: 7px 12px !important;
    box-shadow: none !important;
    position: relative;
}

[data-testid="stChatInput"] textarea {
    color: #ECECEC !important;
    font-size: 15px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #999999 !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #777777 !important;
}

/* SEND BUTTON */

[data-testid="stChatInput"] button {
    background: #ECECEC !important;
    color: #171717 !important;
    border-radius: 50% !important;
}

/* SIDEBAR TEXT */

.sidebar-brand {
    font-size: 20px;
    font-weight: 650;
    letter-spacing: -0.5px;
    padding: 5px 5px 22px;
    color: #F0F0F0;
}

.sidebar-label {
    color: #888888;
    font-size: 12px;
    padding: 20px 8px 8px;
}

/* GENERAL TEXT */

.stMarkdown {
    color: #ECECEC;
}

hr {
    border-color: #383838 !important;
}

/* DISCLAIMER */

.disclaimer {
    text-align: center;
    color: #858585;
    font-size: 11px;
    padding: 12px 0;
}

/* MOBILE DESIGN */

@media screen and (max-width: 768px) {

    .block-container {
        padding: 0.8rem 1rem 1rem;
    }

    .welcome-screen {
        padding-top: 22vh;
    }

    .welcome-screen h1 {
        font-size: 25px;
    }

    [class*="st-key-assistant_"] {
        font-size: 15px;
    }

    .user-bubble {
        font-size: 14px;
    }

}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 4. SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">GhimireyGPT</div>',
        unsafe_allow_html=True
    )

    if st.button("+  New chat", use_container_width=True):

        st.session_state.chat_counter += 1

        new_name = f"New chat {st.session_state.chat_counter}"

        st.session_state.chats[new_name] = []

        st.session_state.current_chat = new_name

        st.rerun()

    st.markdown(
        '<div class="sidebar-label">Your chats</div>',
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


# ==========================================
# 5. MAIN HEADER
# ==========================================

st.markdown(
    '<div class="brand-title">GhimireyGPT</div>',
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)


# ==========================================
# 6. CURRENT CONVERSATION
# ==========================================

messages = st.session_state.chats[
    st.session_state.current_chat
]


# ==========================================
# 7. WELCOME SCREEN
# ==========================================

if len(messages) == 0:

    st.markdown("""
    <div class="welcome-screen">
        <h1>What's on your mind?</h1>
        <p>Ask anything. Let's figure it out together.</p>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 8. DISPLAY EXISTING MESSAGES
# ==========================================

for index, msg in enumerate(messages):

    if msg["role"] == "user":

        with st.container(key=f"user_{index}"):

            safe_text = html.escape(msg["content"]).replace(
                "\n", "<br>"
            )

            st.markdown(
                f'<div class="user-bubble">{safe_text}</div>',
                unsafe_allow_html=True
            )

    else:

        with st.container(key=f"assistant_{index}"):

            st.markdown(msg["content"])


# ==========================================
# 9. MESSAGE INPUT
# ==========================================

prompt = st.chat_input(
    "How's your day going?"
)


# ==========================================
# 10. PROCESS MESSAGE
# ==========================================

if prompt:

    messages = st.session_state.chats[
        st.session_state.current_chat
    ]

    messages.append({
        "role": "user",
        "content": prompt
    })

    # AUTOMATIC CHAT TITLE

    if len(messages) == 1:

        old_name = st.session_state.current_chat

        new_name = prompt.strip()[:32]

        if not new_name:
            new_name = "New conversation"

        if new_name in st.session_state.chats:

            st.session_state.chat_counter += 1

            new_name = (
                f"{new_name} "
                f"({st.session_state.chat_counter})"
            )

        st.session_state.chats[new_name] = messages

        del st.session_state.chats[old_name]

        st.session_state.current_chat = new_name

    # GET AI RESPONSE

    if not API_KEY:

        st.error(
            "API key missing. Please check Streamlit Secrets."
        )

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
                        "You are a highly capable, intelligent and "
                        "natural conversational AI assistant. "
                        "Respond like a thoughtful person. "
                        "Be clear, helpful and direct. "
                        "Avoid unnecessary robotic introductions, "
                        "generic filler and excessive headings. "
                        "Adapt your response to the user's tone."
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

            with st.spinner("Thinking..."):

                response = llm.invoke(conversation)

            answer = response.content

            if isinstance(answer, list):

                answer = "\n".join(
                    str(item.get("text", item))
                    if isinstance(item, dict)
                    else str(item)
                    for item in answer
                )

            messages.append({
                "role": "assistant",
                "content": str(answer)
            })

        except Exception as error:

            st.error(f"Something went wrong: {error}")

    st.rerun()


# ==========================================
# 11. DISCLAIMER
# ==========================================

st.markdown(
    '<div class="disclaimer">'
    'GhimireyGPT can make mistakes. Check important information.'
    '</div>',
    unsafe_allow_html=True
)
