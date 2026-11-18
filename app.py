
import os
import requests
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "openrouter/free"

# ==========================================
# FRONTEND
# ==========================================

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#212121">
<title>GhimireyGPT</title>

<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.2.6/dist/purify.min.js"></script>

<style>
:root {
    --bg: #212121;
    --sidebar: #171717;
    --panel: #303030;
    --border: #393939;
    --text: #ececec;
    --muted: #999999;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Roboto, Helvetica, Arial, sans-serif;
    height: 100dvh;
    overflow: hidden;
}

/* APP LAYOUT */

.app {
    display: flex;
    width: 100%;
    height: 100dvh;
}

/* SIDEBAR */

.sidebar {
    width: 260px;
    min-width: 260px;
    height: 100%;
    background: var(--sidebar);
    display: flex;
    flex-direction: column;
    padding: 15px 12px;
    transition: margin-left .25s ease;
    z-index: 10;
}

.sidebar.hidden {
    margin-left: -260px;
}

.sidebar-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 5px 7px 22px;
}

.brand {
    font-size: 19px;
    font-weight: 650;
    letter-spacing: -.6px;
}

.icon-button {
    border: 0;
    background: transparent;
    color: #b5b5b5;
    width: 38px;
    height: 38px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

.icon-button:hover {
    background: #303030;
    color: white;
}

.icon-button svg {
    width: 20px;
    height: 20px;
}

.new-chat {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 12px;
    background: transparent;
    color: var(--text);
    border: 0;
    padding: 12px 10px;
    border-radius: 9px;
    font-size: 14px;
    text-align: left;
    cursor: pointer;
}

.new-chat:hover {
    background: #292929;
}

.section-label {
    color: #888;
    font-size: 12px;
    font-weight: 600;
    padding: 23px 10px 10px;
}

.history {
    overflow-y: auto;
    flex: 1;
}

.history-item {
    width: 100%;
    background: transparent;
    color: #d5d5d5;
    border: 0;
    border-radius: 8px;
    padding: 10px;
    font-size: 13px;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
}

.history-item:hover,
.history-item.active {
    background: #303030;
}

.sidebar-bottom {
    color: #777;
    font-size: 11px;
    padding: 12px 9px 5px;
}

/* MAIN */

.main {
    flex: 1;
    min-width: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
}

.topbar {
    height: 58px;
    min-height: 58px;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 22px;
    background: var(--bg);
}

.topbar-title {
    font-size: 16px;
    font-weight: 600;
}

/* CONVERSATION */

.conversation {
    flex: 1;
    overflow-y: auto;
    scroll-behavior: smooth;
    padding: 25px 20px 190px;
}

.messages {
    width: 100%;
    max-width: 760px;
    margin: 0 auto;
}

.welcome {
    min-height: 58vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 25px 10px;
}

.welcome h1 {
    font-size: 30px;
    font-weight: 600;
    letter-spacing: -1px;
    margin: 0 0 12px;
}

.welcome p {
    color: var(--muted);
    font-size: 14px;
    margin: 0;
}

.suggestions {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 9px;
    margin-top: 32px;
}

.suggestion {
    color: #d0d0d0;
    background: transparent;
    border: 1px solid #444;
    border-radius: 18px;
    padding: 9px 13px;
    font-size: 12px;
    cursor: pointer;
}

.suggestion:hover {
    background: #303030;
}

/* MESSAGES */

.message {
    width: 100%;
    margin: 0 auto 25px;
    display: flex;
    flex-direction: column;
    animation: appear .2s ease;
}

@keyframes appear {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

.message.user {
    align-items: flex-end;
}

.bubble {
    max-width: 85%;
    overflow-wrap: anywhere;
    line-height: 1.65;
    font-size: 15px;
}

.user .bubble {
    background: #303030;
    padding: 11px 17px;
    border-radius: 20px;
}

.assistant .bubble {
    max-width: 100%;
    padding: 3px 0;
    line-height: 1.75;
    font-size: 15.5px;
}

.assistant .bubble p {
    margin: 0 0 15px;
}

.assistant .bubble pre {
    background: #151515;
    border: 1px solid #404040;
    padding: 15px;
    border-radius: 12px;
    overflow-x: auto;
}

.assistant .bubble code {
    background: #353535;
    padding: 2px 5px;
    border-radius: 4px;
}

.assistant .bubble pre code {
    background: transparent;
    padding: 0;
}

.assistant .bubble h1,
.assistant .bubble h2,
.assistant .bubble h3 {
    font-size: 19px;
    margin: 22px 0 12px;
}

.assistant .bubble ul,
.assistant .bubble ol {
    padding-left: 24px;
}

.assistant .bubble blockquote {
    border-left: 3px solid #666;
    margin-left: 0;
    padding-left: 15px;
    color: #bdbdbd;
}

.message-actions {
    display: flex;
    gap: 5px;
    margin-top: 8px;
    opacity: .6;
}

.message-actions button {
    color: #aaa;
    background: transparent;
    border: 0;
    cursor: pointer;
    padding: 5px;
    border-radius: 6px;
}

.message-actions button:hover {
    background: #333;
    color: white;
}

.message-actions svg {
    width: 16px;
    height: 16px;
}

/* THINKING */

.thinking {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 12px 0;
}

.thinking span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #aaa;
    animation: pulse 1s infinite alternate;
}

.thinking span:nth-child(2) {
    animation-delay: .2s;
}

.thinking span:nth-child(3) {
    animation-delay: .4s;
}

@keyframes pulse {
    from { opacity: .25; }
    to { opacity: 1; }
}

/* COMPOSER */

.composer-area {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 20px 18px 12px;
    background: linear-gradient(
        to bottom,
        rgba(33,33,33,0),
        #212121 23%
    );
    z-index: 5;
}

.composer-wrap {
    max-width: 760px;
    margin: auto;
}

.composer {
    min-height: 58px;
    display: flex;
    align-items: flex-end;
    gap: 10px;
    padding: 10px 12px 10px 18px;
    background: #303030;
    border: 1px solid #454545;
    border-radius: 28px;
    transition: border-color .2s;
}

.composer:focus-within {
    border-color: #686868;
}

.composer textarea {
    flex: 1;
    min-width: 0;
    resize: none;
    outline: none;
    border: 0;
    background: transparent;
    color: #fff;
    font-family: inherit;
    font-size: 15px;
    line-height: 1.5;
    padding: 7px 0;
    max-height: 180px;
}

.composer textarea::placeholder {
    color: #999;
}

.send-button {
    width: 34px;
    height: 34px;
    min-width: 34px;
    border: none;
    border-radius: 50%;
    background: #f2f2f2;
    color: #171717;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

.send-button:disabled {
    opacity: .4;
    cursor: default;
}

.send-button svg {
    width: 19px;
    height: 19px;
}

.disclaimer {
    color: #888;
    text-align: center;
    font-size: 10px;
    padding-top: 10px;
}

/* MOBILE */

@media(max-width: 700px) {
    .sidebar {
        position: fixed;
        top: 0;
        bottom: 0;
        left: 0;
        width: 275px;
        min-width: 275px;
        box-shadow: 12px 0 35px rgba(0,0,0,.3);
    }

    .sidebar.hidden {
        margin-left: -290px;
    }

    .topbar {
        padding: 0 12px;
    }

    .conversation {
        padding: 15px 16px 180px;
    }

    .welcome {
        min-height: 55vh;
    }

    .welcome h1 {
        font-size: 25px;
    }

    .suggestion {
        font-size: 11px;
    }

    .composer-area {
        padding: 15px 12px 10px;
    }

    .bubble {
        font-size: 14px;
    }

    .assistant .bubble {
        font-size: 15px;
    }
}

</style>
</head>

<body>

<div class="app">

    <aside class="sidebar" id="sidebar">

        <div class="sidebar-top">
            <div class="brand">GhimireyGPT</div>

            <button class="icon-button" onclick="toggleSidebar()"
                aria-label="Close sidebar">
                <svg viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="1.8">
                    <rect x="3" y="4" width="18" height="16" rx="2"/>
                    <path d="M9 4v16"/>
                </svg>
            </button>
        </div>

        <button class="new-chat" onclick="newChat()">
            <svg width="19" height="19" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M12 5v14M5 12h14"/>
            </svg>
            New chat
        </button>

        <div class="section-label">Your chats</div>

        <div class="history" id="history"></div>

        <div class="sidebar-bottom">GhimireyGPT</div>

    </aside>

    <main class="main">

        <header class="topbar">

            <button class="icon-button" onclick="toggleSidebar()"
                aria-label="Open sidebar">
                <svg viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="1.8">
                    <rect x="3" y="4" width="18" height="16" rx="2"/>
                    <path d="M9 4v16"/>
                </svg>
            </button>

            <div class="topbar-title">GhimireyGPT</div>

        </header>

        <section class="conversation" id="conversation">

            <div class="messages" id="messages">

                <div class="welcome" id="welcome">

                    <h1>What can I help with?</h1>

                    <p>Ask anything. Let's figure it out together.</p>

                    <div class="suggestions">

                        <button class="suggestion"
                            onclick="useSuggestion('Explain something interesting to me')">
                            Explain something
                        </button>

                        <button class="suggestion"
                            onclick="useSuggestion('Help me write something')">
                            Help me write
                        </button>

                        <button class="suggestion"
                            onclick="useSuggestion('Give me some creative ideas')">
                            Brainstorm ideas
                        </button>

                        <button class="suggestion"
                            onclick="useSuggestion('Help me write some code')">
                            Code with me
                        </button>

                    </div>

                </div>

            </div>

        </section>

        <div class="composer-area">

            <div class="composer-wrap">

                <form class="composer" id="chatForm">

                    <textarea
                        id="prompt"
                        rows="1"
                        placeholder="How's your day going?"
                        aria-label="Message GhimireyGPT"
                    ></textarea>

                    <button class="send-button" id="sendButton"
                        type="submit" aria-label="Send message">

                        <svg viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <path d="M12 19V5M5 12l7-7 7 7"/>
                        </svg>

                    </button>

                </form>

                <div class="disclaimer">
                    GhimireyGPT can make mistakes. Check important information.
                </div>

            </div>

        </div>

    </main>

</div>

<script>

// ==========================================
// LOCAL CONVERSATION STORAGE
// ==========================================

const STORAGE_KEY = "ghimireygpt_chats_v1";

let chats = {};
let currentChat = null;
let busy = false;

try {
    chats = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
} catch (e) {
    chats = {};
}

function saveChats() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
}

function makeId() {
    return "chat_" + Date.now() + "_" +
        Math.random().toString(36).slice(2, 8);
}

function newChat() {
    currentChat = makeId();

    chats[currentChat] = {
        title: "New chat",
        messages: []
    };

    saveChats();
    renderChat();
    renderHistory();

    document.getElementById("prompt").focus();
}

function ensureChat() {
    if (!currentChat || !chats[currentChat]) {
        newChat();
    }
}

// ==========================================
// SIDEBAR
// ==========================================

function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("hidden");
}

function renderHistory() {
    const history = document.getElementById("history");
    history.innerHTML = "";

    Object.keys(chats).reverse().forEach(id => {
        const button = document.createElement("button");

        button.className = "history-item" +
            (id === currentChat ? " active" : "");

        button.textContent = chats[id].title || "New chat";

        button.onclick = () => {
            currentChat = id;
            renderChat();
            renderHistory();

            if (window.innerWidth <= 700) {
                document.getElementById("sidebar")
                    .classList.add("hidden");
            }
        };

        history.appendChild(button);
    });
}

// ==========================================
// MESSAGE RENDERING
// ==========================================

function formatAssistant(text) {
    if (window.marked && window.DOMPurify) {
        return DOMPurify.sanitize(marked.parse(text));
    }

    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, "<br>");
}

function addMessage(role, text, save = true) {
    const messages = document.getElementById("messages");
    const welcome = document.getElementById("welcome");

    if (welcome) welcome.remove();

    const wrapper = document.createElement("div");
    wrapper.className = "message " + role;

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    if (role === "assistant") {
        bubble.innerHTML = formatAssistant(text);
    } else {
        bubble.textContent = text;
    }

    wrapper.appendChild(bubble);

    if (role === "assistant") {
        const actions = document.createElement("div");
        actions.className = "message-actions";

        const copy = document.createElement("button");
        copy.title = "Copy response";
        copy.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="1.8">
                <rect x="8" y="8" width="12" height="12" rx="2"/>
                <path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>
            </svg>
        `;

        copy.onclick = async () => {
            try {
                await navigator.clipboard.writeText(text);
                copy.style.color = "#fff";
                setTimeout(() => copy.style.color = "", 900);
            } catch (e) {}
        };

        actions.appendChild(copy);
        wrapper.appendChild(actions);
    }

    messages.appendChild(wrapper);
    scrollToBottom();
}

function renderChat() {
    const messages = document.getElementById("messages");

    messages.innerHTML = "";

    if (!currentChat || !chats[currentChat]) {
        messages.innerHTML = `
            <div class="welcome" id="welcome">
                <h1>What can I help with?</h1>
                <p>Ask anything. Let's figure it out together.</p>
            </div>
        `;
        return;
    }

    const chat = chats[currentChat];

    if (chat.messages.length === 0) {
        messages.innerHTML = `
            <div class="welcome" id="welcome">
                <h1>What can I help with?</h1>
                <p>Ask anything. Let's figure it out together.</p>
                <div class="suggestions">
                    <button class="suggestion"
                        onclick="useSuggestion('Explain something interesting to me')">
                        Explain something
                    </button>
                    <button class="suggestion"
                        onclick="useSuggestion('Help me write something')">
                        Help me write
                    </button>
                    <button class="suggestion"
                        onclick="useSuggestion('Give me some creative ideas')">
                        Brainstorm ideas
                    </button>
                    <button class="suggestion"
                        onclick="useSuggestion('Help me write some code')">
                        Code with me
                    </button>
                </div>
            </div>
        `;
        return;
    }

    chat.messages.forEach(msg => {
        addMessage(msg.role, msg.content, false);
    });

    scrollToBottom();
}

function scrollToBottom() {
    const conversation = document.getElementById("conversation");

    requestAnimationFrame(() => {
        conversation.scrollTop = conversation.scrollHeight;
    });
}

// ==========================================
// SUGGESTIONS
// ==========================================

function useSuggestion(text) {
    document.getElementById("prompt").value = text;
    document.getElementById("chatForm").requestSubmit();
}

// ==========================================
// THINKING INDICATOR
// ==========================================

function showThinking() {
    const messages = document.getElementById("messages");

    const indicator = document.createElement("div");
    indicator.className = "thinking";
    indicator.id = "thinking";

    indicator.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

    messages.appendChild(indicator);
    scrollToBottom();
}

function removeThinking() {
    const indicator = document.getElementById("thinking");
    if (indicator) indicator.remove();
}

// ==========================================
// SEND MESSAGE
// ==========================================

async function sendMessage(text) {

    if (busy || !text.trim()) return;

    ensureChat();

    busy = true;

    const input = document.getElementById("prompt");
    const button = document.getElementById("sendButton");

    input.value = "";
    input.style.height = "auto";
    button.disabled = true;

    const chat = chats[currentChat];

    chat.messages.push({
        role: "user",
        content: text
    });

    if (chat.messages.length === 1) {
        chat.title = text.slice(0, 35);
    }

    saveChats();
    renderHistory();

    addMessage("user", text);

    showThinking();

    try {

        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                messages: chat.messages
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong.");
        }

        const answer = data.reply;

        if (!answer) {
            throw new Error("The AI returned an empty response.");
        }

        removeThinking();

        chat.messages.push({
            role: "assistant",
            content: answer
        });

        saveChats();

        addMessage("assistant", answer);

    } catch (error) {

        removeThinking();

        addMessage(
            "assistant",
            "Sorry, something went wrong: " + error.message
        );

    } finally {

        busy = false;
        button.disabled = false;
        input.focus();

    }
}

// ==========================================
// FORM EVENTS
// ==========================================

document.getElementById("chatForm")
    .addEventListener("submit", event => {

        event.preventDefault();

        const input = document.getElementById("prompt");
        const text = input.value.trim();

        sendMessage(text);
    });

const promptInput = document.getElementById("prompt");

promptInput.addEventListener("input", () => {
    promptInput.style.height = "auto";

    promptInput.style.height =
        Math.min(promptInput.scrollHeight, 180) + "px";
});

promptInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        document.getElementById("chatForm").requestSubmit();
    }
});

// ==========================================
// STARTUP
// ==========================================

if (Object.keys(chats).length > 0) {
    currentChat = Object.keys(chats).at(-1);
} else {
    currentChat = makeId();

    chats[currentChat] = {
        title: "New chat",
        messages: []
    };
}

renderHistory();
renderChat();

if (window.innerWidth <= 700) {
    document.getElementById("sidebar").classList.add("hidden");
}

</script>

</body>
</html>
"""


# ==========================================
# 2. HOME PAGE
# ==========================================

@app.route("/")
def home():
    return render_template_string(PAGE)


# ==========================================
# 3. AI BACKEND
# ==========================================

@app.route("/api/chat", methods=["POST"])
def chat():

    if not API_KEY:
        return jsonify({
            "error": "API key is missing from server settings."
        }), 500

    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])

    if not isinstance(messages, list) or not messages:
        return jsonify({
            "error": "No messages were provided."
        }), 400

    if len(messages) > 60:
        messages = messages[-60:]

    safe_messages = [{
        "role": "system",
        "content": (
            "You are a helpful, intelligent, natural conversational "
            "AI assistant. Be clear, direct, thoughtful and friendly. "
            "Adapt to the user's tone. Avoid robotic introductions, "
            "unnecessary filler and excessive headings."
        )
    }]

    for message in messages:

        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")

        if role not in ("user", "assistant"):
            continue

        if not isinstance(content, str):
            continue

        safe_messages.append({
            "role": role,
            "content": content[:20000]
        })

    try:

        result = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "X-Title": "GhimireyGPT"
            },
            json={
                "model": MODEL,
                "messages": safe_messages,
                "temperature": 0.7
            },
            timeout=120
        )

        if not result.ok:

            try:
                details = result.json().get("error", {}).get(
                    "message", "OpenRouter request failed."
                )
            except Exception:
                details = "OpenRouter request failed."

            return jsonify({
                "error": str(details)[:500]
            }), result.status_code

        result_data = result.json()

        reply = result_data["choices"][0]["message"]["content"]

        if isinstance(reply, list):
            reply = "\n".join(
                item.get("text", "")
                for item in reply
                if isinstance(item, dict)
            )

        return jsonify({
            "reply": str(reply)
        })

    except requests.Timeout:

        return jsonify({
            "error": "The AI took too long to respond. Try again."
        }), 504

    except Exception as error:

        app.logger.exception("Chat request failed")

        return jsonify({
            "error": "The server could not complete your request."
        }), 500


# ==========================================
# 4. START SERVER
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
