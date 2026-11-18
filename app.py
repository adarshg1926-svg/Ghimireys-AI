
import os

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

# Load local environment variables
load_dotenv()


# Get API key from Streamlit Secrets or local environment
def get_api_key():
    try:
        key = st.secrets.get("OPENROUTER_API_KEY", "")
        if key:
            return str(key).strip()
    except Exception:
        pass

    return os.getenv("OPENROUTER_API_KEY", "").strip()


# Page configuration
st.set_page_config(
    page_title="Ghimireys AI",
    page_icon="💬",
    layout="centered",
)


# Custom styling
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg,
            #101827 0%,
            #172554 100%
        );
        color: #f8fafc;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 14px;
        padding: 10px 14px;
        background: rgba(15,23,42,0.55);
    }

    [data-testid="stSidebar"] {
        background: #0b1220;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Initialize conversation history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Main heading
st.title("💬 Ghimireys AI")
st.caption(
    "Your personal AI assistant powered by "
    "LangChain and OpenRouter."
)


# Sidebar settings
with st.sidebar:

    st.header("⚙️ Settings")

    saved_api_key = get_api_key()

    api_key_override = st.text_input(
        "API Key Override (optional)",
        type="password",
        help="Leave blank to use your saved Streamlit Secret.",
    )

    api_key = api_key_override.strip() or saved_api_key

    model_name = st.text_input(
        "Model ID",
        value="openrouter/free",
    )

    temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
    )

    system_prompt = st.text_area(
        "Bot Instructions",
        value="You are a helpful, clear, and friendly AI assistant.",
        height=100,
    )

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):
        st.session_state.chat_history = []
        st.rerun()

    st.divider()

    if saved_api_key:
        st.caption("API key loaded successfully.")
    else:
        st.caption(
            "Add OPENROUTER_API_KEY in Streamlit Secrets."
        )


# Display previous messages
for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
user_prompt = st.chat_input("Type your message...")


if user_prompt:

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    if not api_key:

        st.error(
            "API key not found. Please configure "
            "OPENROUTER_API_KEY in Streamlit Secrets."
        )

    elif not model_name.strip():

        st.error("Please enter a valid model ID.")

    else:

        try:

            # Initialize LangChain model
            llm = ChatOpenAI(
                model=model_name.strip(),
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=temperature,
                default_headers={
                    "HTTP-Referer": "https://share.streamlit.io/",
                    "X-Title": "Ghimireys AI",
                },
            )

            # Prepare conversation messages
            messages = [
                SystemMessage(content=system_prompt)
            ]

            for item in st.session_state.chat_history:

                if item["role"] == "user":

                    messages.append(
                        HumanMessage(content=item["content"])
                    )

                elif item["role"] == "assistant":

                    messages.append(
                        AIMessage(content=item["content"])
                    )

            # Generate response
            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    response = llm.invoke(messages)

                answer = response.content

                if isinstance(answer, list):

                    answer = "\n".join(
                        block.get("text", str(block))
                        if isinstance(block, dict)
                        else str(block)
                        for block in answer
                    )

                answer = str(answer)

                st.markdown(answer)

            # Save assistant response
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except Exception as error:

            st.error(
                f"OpenRouter request failed: {error}"
            )

            st.caption(
                "Check your API key, model ID, internet "
                "connection, and OpenRouter model availability."
            )
