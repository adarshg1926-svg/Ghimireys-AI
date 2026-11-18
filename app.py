
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

# ==========================================
# 1. CONFIGURATION
# ==========================================

load_dotenv()

st.set_page_config(
    page_title="GhimireyGPT",
    page_icon="G",
    layout="wide",
    initial_sidebar_state="collapsed"
)

try:
    API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
except Exception:
    API_KEY = os.getenv("OPENROUTER_API_KEY", "")

MODEL = "openrouter/free"


# ==========================================
# 2. SESSION STATE
# ==========================================

if "chats" not in st.session_state:
    st.session_state.chats = {
        "New chat": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New chat"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0


# ==========================================
# 3. CUSTOM CSS
# ==========================================

st.markdown("""
<style>

/* GLOBAL */

.stApp {
    background: #212121;
    color: #ECECEC;
}

header, footer, #MainMenu,
.stDeployButton {
    display: none !important;
}

[data-testid="stToolbar"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

.block-container {
    max-width: 850px;
    padding-top: 1rem;
    padding-bottom: 7rem;
}

/* REMOVE UNNECESSARY ELEMENTS */

[data-testid="stDecoration"] {
    display: none !important;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #171717;
    border-right: 1px solid #333333;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.2rem 1rem;
}

section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    color: #EAEAEA !important;
    border: none !important;
    border-radius: 9px !important;
    text-align: left !important;
    padding: 10px 12px !important;
    font-size: 14px !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: #303030 !important;
}

/* BRAND */

.brand {
    font-size: 20px;
    font-weight: 650;
    letter-spacing: -0.7px;
    color: #F0F0F0;
    padding: 5px 5px 22px;
}

.history-label {
    color: #888888;
    font-size: 12px;
    padding: 22px 8px 9px;
}

/* TOP BAR */

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 3px 0 12px;
    border-bottom: 1px solid #333333;
    margin-bottom: 12px;
}

.topbar-title {
    font-size: 16px;
    font-weight: 600;
    color: #ECECEC;
}

/* WELCOME */

.welcome {
    min-height: 55vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.welcome h1 {
    font-size: 30px;
    font-weight: 600;
    letter-spacing: -1px;
    color: #ECECEC;
    margin-bottom: 9px;
}

.welcome p {
    font-size: 14px;
    color: #999999;
}

/* SUGGESTIONS */

.suggestions {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 9px;
    margin-top: 25px;
}

.suggestion {
    border: 1px solid #454545;
    color: #D0D0D0;
    border-radius: 20px;
    padding: 9px 13px;
    font-size: 12px;
    background: transparent;
}

/* USER MESSAGE */

.user-row {
    display: flex;
    justify-content: flex-end;
    width: 100%;
    margin: 24px 0;
}

.user-bubble {
    max-width: 85%;
    background: #303030;
    color: #ECECEC;
    border-radius: 20px;
    padding: 12px 17px;
    font-size: 15px;
    line-height: 1.65;
    overflow-wrap: anywhere;
}

/* ASSISTANT MESSAGE */

.assistant-content {
    color: #ECECEC;
    font-size: 15.5px;
    line-height: 1.8;
    padding: 5px 0;
    overflow-wrap: anywhere;
}

.assistant-content p {
    margin-bottom: 15px;
}

.assistant-content h1,
.assistant-content h2,
.assistant-content h3 {
    color: #F0F0F0;
}

.assistant-content pre {
    background: #151515;
    border: 1px solid #404040;
    border-radius: 12px;
    padding: 14px;
    overflow-x: auto;
}

.assistant-content code {
    background: #353535;
    border-radius: 4px;
    padding: 2px 5px;
}

.assistant-content pre code {
    background: transparent;
    padding: 0;
}

/* CHAT INPUT */

[data-testid="stChatInput"] {
    background: #303030 !important;
    border: 1px solid #454545 !important;
    border-radius: 26px !important;
    box-shadow: none !important;
    padding: 8px 12px !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #777777 !important;
}

[data-testid="stChatInput"] textarea {
    color: #FFFFFF !important;
    font-size: 15px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #999999 !important;
}

[data-testid="stChatInput"] button {
    background: #F0F0F0 !important;
    color: #171717 !important;
    border-radius: 50% !important;
}

/* THINKING */

.stSpinner > div {
    border-top-color: #FFFFFF !important;
}

/* FOOTER */

.disclaimer {
    color: #858585;
    font-size: 11px;
    text-align: center;
    padding: 12px 0;
}

/* MOBILE */

@media(max-width: 768px) {

    .block-container {
        padding: 0.7rem 1rem 6rem;
    }

    .welcome {
        min-height: 55vh;
    }

    .welcome h1 {
        font-size: 25px;
    }

    .assistant-content {
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


# ==========================================
# 5. MAIN HEADER
# ==========================================

st.markdown("""
<div class="topbar">
    <div class="topbar-title">GhimireyGPT</div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 6. CURRENT CHAT
# ==========================================

messages = st.session_state.chats[
    st.session_state.current_chat
]


# ==========================================
# 7. WELCOME SCREEN
# ==========================================

if not messages:

    st.markdown("""
    <div class="welcome">

        <h1>What can I help with?</h1>

        <p>Ask anything. Let's figure it out together.</p>

    </div>
    """, unsafe_allow_html=True)

    # Suggested prompts

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Explain something interesting", use_container_width=True):
            st.session_state.suggested_prompt = "Explain something interesting to me."
            st.rerun()

    with col2:
        if st.button("Help me write something", use_container_width=True):
            st.session_state.suggested_prompt = "Help me write something."
            st.rerun()


# ==========================================
# 8. DISPLAY MESSAGES
# ==========================================

for message in messages:

    if message["role"] == "user":

        safe_text = html.escape(
            message["content"]
        ).replace("\n", "<br>")

        st.markdown(
            f"""
            <div class="user-row">
                <div class="user-bubble">{safe_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="assistant-content">',
            unsafe_allow_html=True
        )

        st.markdown(message["content"])

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ==========================================
# 9. MESSAGE INPUT
# ==========================================

if "suggested_prompt" in st.session_state:

    prompt = st.session_state.pop("suggested_prompt")

else:

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

    # Rename first conversation

    if len(messages) == 1:

        old_name = st.session_state.current_chat

        new_name = prompt.strip()[:32] or "New conversation"

        if new_name in st.session_state.chats:

            st.session_state.chat_counter += 1

            new_name = (
                new_name + " " +
                str(st.session_state.chat_counter)
            )

        st.session_state.chats[new_name] = messages

        del st.session_state.chats[old_name]

        st.session_state.current_chat = new_name

    # API KEY CHECK

    if not API_KEY:

        st.error(
            "API key missing. Check your Streamlit Secrets."
        )

    else:

        try:

            llm = ChatOpenAI(
                model=MODEL,
                api_key=API_KEY,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.7,
                timeout=120
            )

            conversation = [
                SystemMessage(
                    content=(
                        "You are a highly intelligent, natural and "
                        "friendly AI assistant. Respond conversationally. "
                        "Be direct, useful and thoughtful. Avoid robotic "
                        "introductions, unnecessary filler and excessive "
                        "headings. Adapt to the user's tone."
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

            st.error(
                f"Something went wrong: {error}"
            )

    st.rerun()


# ==========================================
# 11. FOOTER
# ==========================================

st.markdown(
    '<div class="disclaimer">'
    'GhimireyGPT can make mistakes. Check important information.'
    '</div>',
    unsafe_allow_html=True
)
