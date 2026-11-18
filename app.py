import os

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Load OPENROUTER_API_KEY from a local .env file, if one exists.
load_dotenv()

st.set_page_config(
    page_title="Local AI Chatbot",
    page_icon="💬",
    layout="centered",
)

# ---------- Simple styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #101827 0%, #172554 100%);
        color: #f8fafc;
    }
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }
    [data-testid="stChatMessage"] {
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        padding: 10px 14px;
        background: rgba(15, 23, 42, 0.55);
    }
    [data-testid="stSidebar"] {
        background: #0b1220;
    }
    h1, h2, h3, p, label {
        color: #f8fafc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Session state ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("💬 Local AI Chatbot")
st.caption("A simple Streamlit chatbot powered by LangChain + OpenRouter.")

# ---------- Sidebar settings ----------
with st.sidebar:
    st.header("⚙️ Settings")

    env_key = os.getenv("OPENROUTER_API_KEY", "")
    api_key = st.text_input(
        "OpenRouter API key",
        value=env_key,
        type="password",
        help="You can also save this as OPENROUTER_API_KEY in a .env file.",
    )

    model_name = st.text_input(
        "Model ID",
        value="openrouter/free",
        help=(
            "Enter an OpenRouter model slug. You can change this to any model "
            "available to your OpenRouter account."
        ),
    )

    temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
    )

    system_prompt = st.text_area(
        "Bot instructions",
        value="You are a helpful, clear, and friendly AI assistant.",
        height=100,
    )

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.divider()
    st.caption("Your API key is used locally by this app and is not written into this Python file.")

# ---------- Display previous messages ----------
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- Chat input and LangChain pipeline ----------
user_prompt = st.chat_input("Type your message...")

if user_prompt:
    if not api_key.strip():
        st.warning(
            "Add your OpenRouter API key in the sidebar, or set "
            "OPENROUTER_API_KEY in a .env file."
        )
    elif not model_name.strip():
        st.warning("Enter an OpenRouter model ID in the sidebar.")
    else:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_prompt}
        )

        with st.chat_message("user"):
            st.markdown(user_prompt)

        try:
            llm = ChatOpenAI(
                model=model_name.strip(),
                api_key=api_key.strip(),
                base_url="https://openrouter.ai/api/v1",
                temperature=temperature,
                default_headers={
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "Local Streamlit Chatbot",
                },
            )

            # Convert the Streamlit conversation into LangChain messages.
            lc_messages = [SystemMessage(content=system_prompt)]
            for item in st.session_state.chat_history:
                if item["role"] == "user":
                    lc_messages.append(HumanMessage(content=item["content"]))
                else:
                    lc_messages.append(AIMessage(content=item["content"]))

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = llm.invoke(lc_messages)

                answer = response.content
                if isinstance(answer, list):
                    # Some models return a list of text/content blocks.
                    answer = "\n".join(
                        block.get("text", str(block))
                        if isinstance(block, dict)
                        else str(block)
                        for block in answer
                    )
                answer = str(answer)
                st.markdown(answer)

            st.session_state.chat_history.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as exc:
            st.error(f"Could not get a response from OpenRouter: {exc}")
            st.caption(
                "Check your API key, model ID, internet connection, and "
                "OpenRouter account/model availability."
            )
