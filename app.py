import io
import os
import html
import uuid
import base64

import streamlit as st
import streamlit.components.v1 as components

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# =====================================================
# 1. CONFIGURATION
# =====================================================

load_dotenv()

st.set_page_config(
    page_title="GhimireyGPT",
    page_icon="G",
    layout="wide",
    initial_sidebar_state="auto",
)

try:
    API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
except Exception:
    API_KEY = os.getenv("OPENROUTER_API_KEY", "")

APP_NAME = "G-GPT"
APP_VERSION = "v1.0"

MODEL = "openrouter/free"
BASE_URL = "https://openrouter.ai/api/v1"

SYSTEM_PROMPT = """
Your name is GhimireyGPT.

You are GhimireyGPT, the AI assistant powering the GhimireyGPT project.

IDENTITY RULES:
- Your name is ALWAYS GhimireyGPT.
- Never introduce yourself as ERNIE Bot.
- Never introduce yourself as Wenxin Yiyan.
- Never claim to be ChatGPT, Gemini, Claude, or another AI assistant.
- Never confuse your underlying model with your assistant identity.
- If asked your name, answer: "I'm GhimireyGPT. What can I help you with?"

You may discuss other AI systems when asked,
but your own identity remains GhimireyGPT.

PERSONALITY:
- Be natural, intelligent and conversational.
- Be friendly without excessive flattery.
- Be direct and honest.
- Disagree when the facts support disagreement.
- Avoid robotic introductions.
- Avoid unnecessary filler.
- Use headings only when useful.
- Adapt to the user's communication style.
- Explain difficult things simply.
- Give detailed answers when necessary.
"""

TEXT_TYPES = ["txt", "md", "csv", "json", "py", "js", "html", "css", "xml", "yaml", "yml", "log"]
IMAGE_TYPES = ["png", "jpg", "jpeg", "webp"]
FILE_TYPES = TEXT_TYPES + IMAGE_TYPES + ["pdf"]
MAX_FILE_CHARS = 20000

SUGGESTIONS = [
    ("Explain something interesting", "Explain something interesting to me."),
    ("Help me write something", "Help me write something."),
    ("Teach me a new skill", "Teach me a useful new skill in 10 minutes."),
    ("Plan my day", "Help me plan a productive day."),
]


# =====================================================
# 2. SESSION STATE
# =====================================================

def new_chat():
    chat_id = uuid.uuid4().hex[:8]
    st.session_state.chats[chat_id] = {"title": "New chat", "messages": []}
    st.session_state.current_chat = chat_id


if "chats" not in st.session_state:
    st.session_state.chats = {}
    new_chat()

if "current_chat" not in st.session_state:
    new_chat()

if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = None


# =====================================================
# 3. DESIGN AND CSS
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #212121;
    --bg-sidebar: #171717;
    --bg-input: #2F2F2F;
    --bg-hover: #2A2A2A;
    --bg-user: #2F2F2F;
    --border: #3A3A3A;
    --text: #ECECEC;
    --text-dim: #9B9B9B;
    --accent: #FFFFFF;
}

html, body, .stApp, [class*="st-"], button, input, textarea {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ---------- PAGE ---------- */

.stApp {
    background: var(--bg);
    color: var(--text);
}

header[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"],
[data-testid="stDeployButton"],
[data-testid="stDecoration"],
#MainMenu,
footer {
    display: none !important;
}

.block-container {
    max-width: 768px;
    padding: 4.5rem 1.25rem 9rem;
}

/* ---------- FIXED TOP HEADER ---------- */

.app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 56px;
    z-index: 999980;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: linear-gradient(to bottom, var(--bg) 70%, rgba(33,33,33,0));
    pointer-events: none;
}

.app-header .app-name {
    font-size: 17px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: #FFFFFF;
}

.app-header .app-version {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-dim);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 2px 8px;
}

@media (min-width: 769px) {
    .stApp:has(section[data-testid="stSidebar"][aria-expanded="true"]) .app-header {
        left: 21rem;
    }
}

/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: var(--bg-sidebar);
    border-right: none;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1rem 0.75rem;
}

section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    color: var(--text) !important;
    border: none !important;
    border-radius: 10px !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 9px 12px !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    box-shadow: none !important;
    transition: background 0.15s ease;
}

section[data-testid="stSidebar"] .stButton button p {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: var(--bg-hover) !important;
}

div.st-key-new_chat button {
    font-weight: 500 !important;
    border: 1px solid var(--border) !important;
    margin-bottom: 6px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 17px;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: var(--text);
    padding: 4px 8px 18px;
}

.brand-mark, .assistant-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--accent);
    color: #171717;
    font-size: 14px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.history-label {
    color: var(--text-dim);
    font-size: 12px;
    font-weight: 500;
    padding: 18px 12px 6px;
}

/* ---------- WELCOME ---------- */

.welcome {
    min-height: 38vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 4vh 8px 2vh;
}

.welcome h1 {
    font-size: clamp(26px, 5vw, 34px);
    font-weight: 600;
    letter-spacing: -0.8px;
    line-height: 1.2;
    color: var(--text);
    margin: 0 0 10px;
    padding: 0;
}

.welcome p {
    color: var(--text-dim);
    font-size: 15px;
    margin: 0;
}

[class*="st-key-suggest_"] button {
    background: transparent !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    min-height: 54px;
    padding: 10px 16px !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    justify-content: flex-start !important;
    text-align: left !important;
    transition: background 0.15s ease;
}

[class*="st-key-suggest_"] button:hover {
    background: var(--bg-hover) !important;
    border-color: #555 !important;
}

/* ---------- MESSAGES ---------- */

.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 18px 0;
}

.user-bubble {
    max-width: 80%;
    background: var(--bg-user);
    color: var(--text);
    border-radius: 22px;
    padding: 10px 18px;
    font-size: 15.5px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

[class*="st-key-assistant_"] {
    position: relative;
    padding-left: 42px;
    margin: 10px 0 18px;
}

[class*="st-key-assistant_"]::before {
    content: "G";
    position: absolute;
    left: 0;
    top: 2px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--accent);
    color: #171717;
    font-size: 14px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}

[class*="st-key-assistant_"] [data-testid="stMarkdownContainer"] {
    color: var(--text);
    font-size: 15.5px;
    line-height: 1.75;
    overflow-wrap: anywhere;
}

[class*="st-key-assistant_"] p {
    margin: 0 0 12px;
}

[class*="st-key-assistant_"] h1,
[class*="st-key-assistant_"] h2,
[class*="st-key-assistant_"] h3 {
    color: #FFFFFF;
    font-weight: 600;
    letter-spacing: -0.3px;
    margin: 20px 0 8px;
    padding: 0;
}

[class*="st-key-assistant_"] h1 { font-size: 22px; }
[class*="st-key-assistant_"] h2 { font-size: 19px; }
[class*="st-key-assistant_"] h3 { font-size: 16.5px; }

[class*="st-key-assistant_"] li {
    margin-bottom: 4px;
}

[class*="st-key-assistant_"] a {
    color: #9CC9FF;
}

[class*="st-key-assistant_"] pre {
    background: #171717 !important;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 16px;
}

[class*="st-key-assistant_"] code {
    font-family: 'JetBrains Mono', ui-monospace, monospace !important;
    font-size: 13.5px;
    background: #303030;
    border-radius: 6px;
    padding: 2px 6px;
}

[class*="st-key-assistant_"] pre code {
    background: transparent;
    padding: 0;
}

[class*="st-key-assistant_"] table {
    border-collapse: collapse;
}

[class*="st-key-assistant_"] th,
[class*="st-key-assistant_"] td {
    border: 1px solid var(--border);
    padding: 8px 12px;
}

.file-chips {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 6px;
    margin: 18px 0 -8px;
}

.file-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    max-width: 240px;
    background: var(--bg-user);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 6px 10px;
    font-size: 13px;
    color: var(--text);
}

.file-chip span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* ---------- THINKING DOTS ---------- */

.thinking {
    display: flex;
    gap: 5px;
    padding: 12px 0;
}

.thinking span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--text-dim);
    animation: pulse 1.2s infinite ease-in-out;
}

.thinking span:nth-child(2) { animation-delay: 0.15s; }
.thinking span:nth-child(3) { animation-delay: 0.3s; }

@keyframes pulse {
    0%, 80%, 100% { opacity: 0.25; transform: scale(0.8); }
    40% { opacity: 1; transform: scale(1); }
}

@media (prefers-reduced-motion: reduce) {
    .thinking span { animation: none; opacity: 0.6; }
}

/* ---------- CHAT INPUT ---------- */

[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background: var(--bg) !important;
}

[data-testid="stChatInput"] {
    background: var(--bg-input) !important;
    border: 1px solid transparent !important;
    border-radius: 28px !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #555 !important;
}

/* remove Streamlit's red focus outline */
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] textarea {
    border-color: transparent !important;
    box-shadow: none !important;
    outline: none !important;
}

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] textarea {
    background: transparent !important;
}

[data-testid="stChatInput"] textarea {
    color: #FFFFFF !important;
    font-size: 15.5px !important;
    padding: 14px 8px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-dim) !important;
}

[data-testid="stChatInput"] button {
    background: #FFFFFF !important;
    color: #171717 !important;
    border-radius: 50% !important;
}

[data-testid="stChatInput"] button:disabled {
    background: #5A5A5A !important;
    color: #2F2F2F !important;
}

.disclaimer {
    color: #7D7D7D;
    text-align: center;
    font-size: 12px;
    padding: 18px 0 0;
}

/* ---------- MOBILE ---------- */

@media (max-width: 768px) {
    .block-container { padding: 1rem 0.9rem 8rem; }
    .user-bubble { max-width: 90%; font-size: 15px; }
    [class*="st-key-assistant_"] { padding-left: 38px; }
    [class*="st-key-assistant_"] [data-testid="stMarkdownContainer"] { font-size: 15px; }
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 4. HELPERS
# =====================================================

THINKING_HTML = '<div class="thinking"><span></span><span></span><span></span></div>'


CLIP_SVG = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66'
    'l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>'
)


def render_user(text, attachments=None):
    if attachments:
        chips = "".join(
            f'<div class="file-chip">{CLIP_SVG}<span>{html.escape(a["name"])}</span></div>'
            for a in attachments
        )
        st.markdown(f'<div class="file-chips">{chips}</div>', unsafe_allow_html=True)
    if text:
        safe = html.escape(text).replace("\n", "<br>")
        st.markdown(
            f'<div class="user-row"><div class="user-bubble">{safe}</div></div>',
            unsafe_allow_html=True,
        )


def read_attachment(uploaded):
    name = uploaded.name
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    data = uploaded.getvalue()

    if ext in IMAGE_TYPES:
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        return {"name": name, "kind": "image", "mime": mime,
                "data": base64.b64encode(data).decode()}

    if ext == "pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception:
            text = "(Could not read this PDF. Install pypdf or try a text-based PDF.)"
    else:
        text = data.decode("utf-8", errors="replace")

    if len(text) > MAX_FILE_CHARS:
        text = text[:MAX_FILE_CHARS] + "\n...[file truncated]"
    return {"name": name, "kind": "text", "text": text}


def chunk_to_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content or "")


def build_conversation(messages):
    conversation = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in messages:
        if msg["role"] == "user":
            text = msg["content"]
            attachments = msg.get("attachments", [])
            for a in attachments:
                if a["kind"] == "text":
                    text += f"\n\n[Attached file: {a['name']}]\n{a['text']}"
            images = [a for a in attachments if a["kind"] == "image"]
            if images:
                parts = [{"type": "text", "text": text or "Describe this image."}]
                parts += [
                    {"type": "image_url",
                     "image_url": {"url": f"data:{a['mime']};base64,{a['data']}"}}
                    for a in images
                ]
                conversation.append(HumanMessage(content=parts))
            else:
                conversation.append(HumanMessage(content=text))
        else:
            conversation.append(AIMessage(content=msg["content"]))
    return conversation


# =====================================================
# 5. SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">G</span>GhimireyGPT</div>',
        unsafe_allow_html=True,
    )

    if st.button("+  New chat", key="new_chat", use_container_width=True):
        new_chat()
        st.rerun()

    st.markdown('<div class="history-label">Your chats</div>', unsafe_allow_html=True)

    for chat_id in reversed(list(st.session_state.chats.keys())):
        chat = st.session_state.chats[chat_id]

        if chat_id == st.session_state.current_chat:
            st.markdown(
                f"<style>.st-key-chat_{chat_id} button "
                "{ background: #2A2A2A !important; }</style>",
                unsafe_allow_html=True,
            )

        if st.button(chat["title"], key=f"chat_{chat_id}", use_container_width=True):
            st.session_state.current_chat = chat_id
            st.rerun()


st.markdown(
    f'<div class="app-header"><span class="app-name">{APP_NAME}</span>'
    f'<span class="app-version">{APP_VERSION}</span></div>',
    unsafe_allow_html=True,
)


# =====================================================
# 6. CURRENT CONVERSATION
# =====================================================

chat = st.session_state.chats[st.session_state.current_chat]
messages = chat["messages"]

# Welcome screen
if not messages:
    st.markdown(
        """
        <div class="welcome">
            <h1>What can I help with?</h1>
            <p>Ask anything. Let's figure it out together.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    for i, (label, prompt_text) in enumerate(SUGGESTIONS):
        with cols[i % 2]:
            if st.button(label, key=f"suggest_{i}", use_container_width=True):
                st.session_state.suggested_prompt = prompt_text
                st.rerun()

# Past messages
for i, msg in enumerate(messages):
    if msg["role"] == "user":
        render_user(msg["content"], msg.get("attachments"))
    else:
        with st.container(key=f"assistant_{st.session_state.current_chat}_{i}"):
            st.markdown(msg["content"])


# =====================================================
# 7. INPUT
# =====================================================

submitted = st.chat_input(
    "Message GhimireyGPT",
    accept_file="multiple",
)

prompt = None
uploads = []

if st.session_state.suggested_prompt:
    prompt = st.session_state.suggested_prompt
elif submitted:
    prompt = (submitted.text or "").strip()
    uploads = []
    for f in (submitted.files or []):
        ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
        if ext in FILE_TYPES:
            uploads.append(f)
        else:
            st.warning(f"Skipped {f.name}: unsupported file type.")
    if not prompt and submitted.files and not uploads:
        prompt = None

st.session_state.suggested_prompt = None


# =====================================================
# 8. HANDLE NEW MESSAGE (STREAMING)
# =====================================================

if prompt or uploads:
    attachments = [read_attachment(f) for f in uploads]
    messages.append({"role": "user", "content": prompt, "attachments": attachments})
    render_user(prompt, attachments)

    if len(messages) == 1:
        title = (prompt or attachments[0]["name"]).strip().replace("\n", " ")
        chat["title"] = (title[:34] + "…") if len(title) > 34 else title

    if not API_KEY:
        st.error("API key missing. Add OPENROUTER_API_KEY to your Streamlit secrets or .env file.")
    else:
        answer = ""
        with st.container(key=f"assistant_{st.session_state.current_chat}_{len(messages)}"):
            placeholder = st.empty()
            placeholder.markdown(THINKING_HTML, unsafe_allow_html=True)

            try:
                llm = ChatOpenAI(
                    model=MODEL,
                    api_key=API_KEY,
                    base_url=BASE_URL,
                    temperature=0.7,
                    timeout=120,
                    streaming=True,
                )

                for chunk in llm.stream(build_conversation(messages)):
                    answer += chunk_to_text(chunk.content)
                    if answer:
                        placeholder.markdown(answer + " ▌")

                if not answer.strip():
                    answer = "I didn't get a response. Please try again."

                placeholder.markdown(answer)

            except Exception as error:
                answer = (
                    "I couldn't complete that request. Please try again.\n\n"
                    f"`{error}`"
                )
                placeholder.markdown(answer)

        messages.append({"role": "assistant", "content": answer})
        st.rerun()


# =====================================================
# 9. DISCLAIMER + AUTO SCROLL
# =====================================================

if messages:
    st.markdown(
        '<div class="disclaimer">GhimireyGPT can make mistakes. Check important information.</div>',
        unsafe_allow_html=True,
    )

components.html("""
<script>
function scrollToLatest() {
    const doc = window.parent.document;
    const el = doc.querySelector('[data-testid="stMain"]')
            || doc.querySelector('[data-testid="stAppViewContainer"]');
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
}
setTimeout(scrollToLatest, 200);
setTimeout(scrollToLatest, 700);
</script>
""", height=0)
