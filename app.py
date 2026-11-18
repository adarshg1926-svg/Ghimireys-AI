
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

# =========================================
# 1. CONFIGURATION
# =========================================

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


# =========================================
# 2. SESSION STATE
# =========================================

if "chats" not in st.session_state:
    st.session_state.chats = {
        "New chat": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New chat"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = None


# =========================================
# 3. CUSTOM DESIGN
# =========================================

st.markdown("""
<style>

/* Main background */

.stApp {
    background: #212121;
    color: #ECECEC;
}

header[data-testid="stHeader"] {
    background: #212121;
}

[data-testid="stToolbar"],
[data-testid="stDeployButton"],
[data-testid="stDecoration"],
#MainMenu,
footer {
    display: none !important;
}

.block-container {
    max-width: 850px;
    padding: 1rem 1.25rem 7rem;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: #171717;
    border-right: 1px solid #333;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.2rem 1rem;
}

section[data-testid="stSidebar"] .stButton button {
    background: transparent;
    color: #EAEAEA;
    border: none;
    border-radius: 9px;
    text-align: left;
    padding: 10px 12px;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: #303030;
}

/* Branding */

.brand {
    font-size: 21px;
    font-weight: 650;
    letter-spacing: -0.7px;
    padding: 5px 5px 22px;
    color: #F0F0F0;
}

.history-label {
    color: #888;
    font-size: 12px;
    padding: 22px 8px 10px;
}

/* Top bar */

.topbar {
    display: flex;
    align-items: center;
    min-height: 48px;
    border-bottom: 1px solid #383838;
    margin-bottom: 12px;
}

.topbar-title {
    font-size: 17px;
    font-weight: 650;
    color: #F0F0F0;
}

/* Welcome screen */

.welcome {
    width: 100%;
    max-width: 650px;
    min-height: 48vh;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 25px 12px;
}

.welcome h1 {
    font-size: clamp(23px, 5vw, 31px);
    line-height: 1.25;
    font-weight: 600;
    letter-spacing: -1px;
    color: #ECECEC;
    margin: 0 0 12px;
}

.welcome p {
    color: #A0A0A0;
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
    max-width: 100%;
    overflow-wrap: anywhere;
}

/* Suggestions */

div.st-key-suggestion1 button,
div.st-key-suggestion2 button {
    background: transparent;
    color: #D0D0D0;
    border: 1px solid #454545;
    border-radius: 18px;
    min-height: 43px;
    font-size: 12px;
}

div.st-key-suggestion1 button:hover,
div.st-key-suggestion2 button:hover {
    background: #303030;
    border-color: #666;
}

/* User messages */

.user-row {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    margin: 24px 0;
}

.user-bubble {
    max-width: 85%;
    background: #303030;
    color: #ECECEC;
    border-radius: 20px;
    padding: 11px 17px;
    font-size: 15px;
    line-height: 1.65;
    overflow-wrap: anywhere;
    word-break: break-word;
}

/* Assistant messages */

.assistant-content {
    width: 100%;
    color: #ECECEC;
    font-size: 15.5px;
    line-height: 1.8;
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

/* Chat input */

[data-testid="stChatInput"] {
    background: #303030 !important;
    border: 1px solid #454545 !important;
    border-radius: 26px !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #777 !important;
}

[data-testid="stChatInput"] textarea {
    color: white !important;
    font-size: 15px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #999 !important;
}

[data-testid="stChatInput"] button {
    background: #F0F0F0 !important;
    color: #171717 !important;
    border-radius: 50% !important;
}

/* Footer */

.disclaimer {
    color: #858585;
    text-align: center;
    font-size: 10px;
    padding: 10px 0;
}

/* Mobile */

@media (max-width: 768px) {

    .block-container {
        padding: 0.7rem 1rem 6rem;
    }

    .welcome {
        min-height: 43vh;
        padding: 20px 5px;
    }

    .welcome h1 {
        font-size: 25px;
    }

    .welcome p {
        font-size: 13px;
    }

    .user-bubble {
        max-width: 90%;
        font-size: 14px;
    }

    .assistant-content {
        font-size: 15px;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================
# 4. SIDEBAR
# =========================================

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


# =========================================
# 5. HEADER
# =========================================

st.html("""
<div class="topbar">
    <div class="topbar-title">GhimireyGPT</div>
</div>
""")


# =========================================
# 6. GET CURRENT CONVERSATION
# =========================================

current_name = st.session_state.current_chat

messages = st.session_state.chats[current_name]


# =========================================
# 7. WELCOME SCREEN
# =========================================

if not messages:

    st.html("""
    <div class="welcome">
        <h1>What can I help with?</h1>
        <p>Ask anything. Let's figure it out together.</p>
    </div>
    """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Explain something interesting",
            key="suggestion1",
            use_container_width=True
        ):
            st.session_state.suggested_prompt = (
                "Explain something interesting to me."
            )
            st.rerun()

    with col2:
        if st.button(
            "Help me write something",
            key="suggestion2",
            use_container_width=True
        ):
            st.session_state.suggested_prompt = (
                "Help me write something."
            )
            st.rerun()


# =========================================
# 8. DISPLAY CONVERSATION
# =========================================

for message in messages:

    if message["role"] == "user":

        safe_text = html.escape(
            message["content"]
        ).replace("\n", "<br>")

        st.html(
            f"""
            <div class="user-row">
                <div class="user-bubble">{safe_text}</div>
            </div>
            """
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


# =========================================
# 9. MESSAGE INPUT
# =========================================

if st.session_state.suggested_prompt:

    prompt = st.session_state.suggested_prompt

    st.session_state.suggested_prompt = None

else:

    prompt = st.chat_input(
        "How's your day going?"
    )


# =========================================
# 10. SEND TO AI
# =========================================

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

    # API KEY

    if not API_KEY:

        st.error(
            "API key missing. Check Streamlit Secrets."
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
                        "You are GhimireyGPT, a capable and natural "
                        "conversational AI assistant. Be helpful, "
                        "thoughtful, clear and direct. Adapt to the "
                        "user's tone. Avoid robotic introductions, "
                        "unnecessary filler and excessive headings. "
                        "Give honest answers, including disagreement "
                        "when appropriate."
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

        except Exception:

            messages.append({
                "role": "assistant",
                "content": (
                    "I couldn't complete that request. "
                    "Please try again in a moment."
                )
            })

    st.rerun()


# =========================================
# 11. DISCLAIMER
# =========================================

st.html("""
<div class="disclaimer">
    GhimireyGPT can make mistakes. Check important information.
</div>
""")
