# ============================================================
# CITY INTELLIGENCE AI AGENT (SIDEBAR TOGGLE BUTTON FIXED)
# ============================================================

import os
import requests
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
)
from tavily import TavilyClient

# ------------------------------------------------------------
# 1. LOAD ENVIRONMENT & CONFIG
# ------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="City Intelligence AI",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

SYSTEM_PROMPT = SystemMessage(
    content="You are City Intelligence AI. "
    "When asked about a city's weather or news, use the available tools to fetch data. "
    "If multiple tools are called, combine all results cleanly into a single, beautifully structured Markdown response with bold titles, emojis, and clear links. "
    "Do not echo raw JSON or repetition."
)

# ------------------------------------------------------------
# 2. CUSTOM CSS (FIX SIDEBAR BUTTON & KEEP CLEAN LOOK)
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    /* HIDE DEFAULT MENU & DEPLOY BUTTON ONLY (KEEP SIDEBAR TOGGLE VISIBLE) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    
    /* Transparent Top Header (so sidebar toggle button stays visible) */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 100 !important;
    }

    /* Style the Sidebar Toggle Button for Dark Theme */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="baseButton-headerNoPadding"] {
        color: #ffffff !important;
        background-color: #212121 !important;
        border: 1px solid #383838 !important;
        border-radius: 8px !important;
    }

    /* Global App Background & Typography */
    .stApp {
        background-color: #171717 !important;
        color: #ececf1 !important;
        font-family: 'Söhne', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #2f2f2f !important;
    }

    section[data-testid="stSidebar"] * {
        color: #ececf1 !important;
    }

    /* Main Container Padding */
    .main .block-container {
        max-width: 900px !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        margin: 0 auto !important;
    }

    /* Modern Logo Banner Container */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
        padding: 12px 16px;
        background: linear-gradient(135deg, rgba(16, 163, 127, 0.1) 0%, rgba(33, 33, 33, 0.6) 100%);
        border: 1px solid rgba(16, 163, 127, 0.3);
        border-radius: 16px;
    }

    .logo-icon {
        font-size: 38px;
        background: #10a37f;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(16, 163, 127, 0.4);
    }

    .logo-text-title {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .logo-text-sub {
        color: #10a37f;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }

    /* Clean Streamlit Chat Input Box */
    div[data-testid="stChatInput"] {
        background-color: #212121 !important;
        border: 1px solid #383838 !important;
        border-radius: 16px !important;
        padding: 4px 8px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }

    div[data-testid="stChatInput"] > div {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background-color: transparent !important;
        font-size: 15px !important;
        font-family: inherit !important;
        caret-color: #10a37f !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Chat Messages Alignment */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 14px 18px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        width: 100% !important;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message avatar user"]) {
        background-color: #2f2f2f !important;
        border: 1px solid #383838 !important;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message avatar assistant"]) {
        background-color: #212121 !important;
        border: 1px solid #2f2f2f !important;
    }

    /* Cards Styling */
    .info-card {
        padding: 14px 18px;
        border-radius: 12px;
        background-color: #212121 !important;
        border: 1px solid #2f2f2f !important;
        margin-bottom: 12px;
    }

    .card-title {
        font-size: 11px;
        font-weight: 700;
        color: #10a37f !important;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .card-value {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff !important;
    }

    .welcome {
        padding: 28px;
        text-align: center;
        border-radius: 16px;
        background-color: #212121 !important;
        border: 1px solid #2f2f2f !important;
        margin: 15px auto 25px auto;
    }

    .tool-badge {
        display: inline-block;
        padding: 4px 10px;
        margin: 2px;
        border-radius: 12px;
        background-color: #2f2f2f !important;
        border: 1px solid #383838 !important;
        color: #10a37f !important;
        font-size: 12px;
    }

    .stButton > button {
        background-color: #212121 !important;
        color: #ececf1 !important;
        border: 1px solid #383838 !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }

    /* Custom Footer Styling */
    .custom-footer {
        text-align: center;
        color: #8e8ea0;
        padding: 15px 0 5px 0;
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 3. TOOLS DEFINITION WITH CLEAN ERROR HANDLING
# ------------------------------------------------------------
@tool
def get_weather(city: str) -> str:
    """Get current weather of a city using OpenWeather API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Weather service is currently unavailable."

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception:
        return f"Unable to fetch weather details for {city} right now."

    if str(data.get("cod")) != "200":
        return f"Could not find weather information for '{city}'. Please check the city name."

    temperature = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    description = data["weather"][0]["description"].title()

    return f"City: {city.title()} | Weather: {description} | Temp: {temperature}°C (Feels like: {feels_like}°C) | Humidity: {humidity}%"

@tool
def get_news(city: str) -> str:
    """Get latest news about a city using Tavily."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "News service is currently unavailable."

    try:
        tavily_client = TavilyClient(api_key=api_key)
        response = tavily_client.search(
            query=f"latest news in {city}",
            search_depth="basic",
            max_results=3,
        )
    except Exception:
        return f"Unable to fetch latest news for {city} right now."

    results = response.get("results", [])
    if not results:
        return f"No recent news found for {city}."

    news_items = []
    for result in results:
        title = result.get("title", "No title")
        url = result.get("url", "")
        content = result.get("content", "").replace("\n", " ")[:160]
        news_items.append(f"• Headline: {title}\n  Summary: {content}...\n  Link: {url}")

    return "\n\n".join(news_items)

# ------------------------------------------------------------
# 4. INITIALIZE LLM & STATE
# ------------------------------------------------------------
@st.cache_resource
def create_llm():
    return ChatGroq(model="openai/gpt-oss-20b", temperature=0.2)

llm = create_llm()
tools = {"get_weather": get_weather, "get_news": get_news}
llm_with_tools = llm.bind_tools([get_weather, get_news])

if "messages" not in st.session_state:
    st.session_state.messages = [SYSTEM_PROMPT]
if "pending_tool_calls" not in st.session_state:
    st.session_state.pending_tool_calls = []
if "session_approved" not in st.session_state:
    st.session_state.session_approved = False

# ------------------------------------------------------------
# 5. SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.markdown('<div style="font-size:22px; font-weight:700; padding:10px 0 15px 0;">🏙️ City Intelligence</div>', unsafe_allow_html=True)
    st.markdown("### 🧠 AI Agent")
    st.success("● Agent Online")

    st.markdown("### Available Tools")
    st.markdown("""
        <span class="tool-badge">🌤️ Weather</span>
        <span class="tool-badge">📰 News</span>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### ⚙️ Agent Settings")
    approval_mode = st.toggle("Human approval required", value=True, help="Ask approval before tools execute.")

    st.divider()
    if st.button("🗑 Clear Conversation", use_container_width=True):
        st.session_state.messages = [SYSTEM_PROMPT]
        st.session_state.pending_tool_calls = []
        st.session_state.session_approved = False
        st.rerun()

# ------------------------------------------------------------
# 6. HEADER LOGO & METRIC CARDS
# ------------------------------------------------------------
st.markdown("""
    <div class="logo-container">
        <div class="logo-icon">🏙️️</div>
        <div>
            <div class="logo-text-title">City Intelligence AI</div>
            <div class="logo-text-sub">● Real-time Autonomous Agent System</div>
        </div>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="info-card"><div class="card-title">🤖 AI MODEL</div><div class="card-value">GPT-OSS-20B</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="info-card"><div class="card-title">🛠 ACTIVE TOOLS</div><div class="card-value">2 Enabled</div></div>', unsafe_allow_html=True)
with col3:
    if st.session_state.session_approved:
        status = "Authorized Mode"
    else:
        status = "Approval ON" if approval_mode else "Auto Execute"
    st.markdown(f'<div class="info-card"><div class="card-title">🔐 EXECUTION MODE</div><div class="card-value">{status}</div></div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 7. WELCOME & QUICK PROMPTS
# ------------------------------------------------------------
if len(st.session_state.messages) <= 1:
    st.markdown("""
        <div class="welcome">
            <h2 style="margin-bottom:8px;">👋 Welcome to City Intelligence</h2>
            <p style="color:#8e8ea0;">Select a quick prompt or type a message below.</p>
        </div>
    """, unsafe_allow_html=True)

    prompt_col1, prompt_col2, prompt_col3 = st.columns(3)
    with prompt_col1:
        if st.button("🌤 Weather in Meerut", use_container_width=True):
            st.session_state.pending_prompt = "What is the current weather in Meerut?"
            st.rerun()
    with prompt_col2:
        if st.button("📰 Latest Meerut News", use_container_width=True):
            st.session_state.pending_prompt = "What is the latest news in Meerut?"
            st.rerun()
    with prompt_col3:
        if st.button("🌍 Meerut Intelligence", use_container_width=True):
            st.session_state.pending_prompt = "Give me the current weather and latest news in Meerut."
            st.rerun()

# ------------------------------------------------------------
# 8. RENDER CHAT HISTORY
# ------------------------------------------------------------
for message in st.session_state.messages:
    if isinstance(message, SystemMessage):
        continue
        
    if isinstance(message, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            st.markdown(message.content)
            
    elif isinstance(message, AIMessage):
        if message.content and str(message.content).strip():
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message.content)

# ------------------------------------------------------------
# 9. HELPER FUNCTION TO EXECUTE TOOLS & GENERATE RESPONSE
# ------------------------------------------------------------
def process_tool_execution():
    while st.session_state.pending_tool_calls:
        tool_calls = list(st.session_state.pending_tool_calls)
        st.session_state.pending_tool_calls = []

        for tc in tool_calls:
            tool_name = tc["name"]
            tool_args = tc["args"]
            tool_call_id = tc["id"]

            with st.spinner(f"Fetching data via {tool_name}..."):
                if tool_name in tools:
                    try:
                        tool_result = tools[tool_name].invoke(tool_args)
                    except Exception:
                        tool_result = "Something went wrong while fetching data."
                else:
                    tool_result = "Requested service is temporarily unavailable."

            st.session_state.messages.append(
                ToolMessage(content=str(tool_result), tool_call_id=tool_call_id)
            )

        with st.spinner("🤖 Compiling final response..."):
            try:
                final_res = llm_with_tools.invoke(st.session_state.messages)
                st.session_state.messages.append(final_res)

                new_tool_calls = getattr(final_res, "tool_calls", None)
                if new_tool_calls:
                    st.session_state.pending_tool_calls = new_tool_calls
            except Exception:
                st.session_state.messages.append(
                    AIMessage(content="Sorry, I encountered an issue while generating the response. Please try again.")
                )
                break

# ------------------------------------------------------------
# 10. APPROVAL UI OR AUTO EXECUTION
# ------------------------------------------------------------
if st.session_state.pending_tool_calls:
    if approval_mode and not st.session_state.session_approved:
        with st.chat_message("assistant", avatar="🤖"):
            st.warning("🔐 **Action Approval Required**")
            st.write("The AI Agent requests approval to run tools:")
            for idx, tc in enumerate(st.session_state.pending_tool_calls, start=1):
                st.markdown(f"**{idx}. Tool:** `{tc['name']}`")
                st.json(tc.get("args", {}))

            col_approve, col_approve_session, col_deny = st.columns([1, 1.2, 1])
            
            with col_approve:
                if st.button("✅ Approve Once", use_container_width=True, key="btn_approve"):
                    process_tool_execution()
                    st.rerun()

            with col_approve_session:
                if st.button("⚡ Approve for Entire Session", use_container_width=True, key="btn_approve_session"):
                    st.session_state.session_approved = True
                    process_tool_execution()
                    st.rerun()

            with col_deny:
                if st.button("❌ Deny Request", use_container_width=True, key="btn_deny"):
                    for tc in st.session_state.pending_tool_calls:
                        st.session_state.messages.append(
                            ToolMessage(content="User cancelled execution.", tool_call_id=tc["id"])
                        )
                    st.session_state.pending_tool_calls = []
                    st.rerun()
    else:
        process_tool_execution()
        st.rerun()

# ------------------------------------------------------------
# 11. CUSTOM FOOTER
# ------------------------------------------------------------
st.markdown("""
    <div class="custom-footer">
        City Intelligence AI Agent • Streamlit & LangChain Architecture
    </div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 12. PROCESS USER INPUT
# ------------------------------------------------------------
pending_prompt = st.session_state.pop("pending_prompt", None)
user_prompt = st.chat_input("Ask about a city...")

if pending_prompt:
    user_prompt = pending_prompt

if user_prompt:
    st.session_state.messages.append(HumanMessage(content=user_prompt))

    with st.spinner("🧠 Analyzing request..."):
        try:
            result = llm_with_tools.invoke(st.session_state.messages)
            st.session_state.messages.append(result)

            tool_calls = getattr(result, "tool_calls", None)
            if tool_calls:
                st.session_state.pending_tool_calls = tool_calls
                if not approval_mode or st.session_state.session_approved:
                    process_tool_execution()

            st.rerun()
        except Exception:
            st.session_state.messages.append(
                AIMessage(content="Something went wrong while connecting to the assistant. Please try again in a moment.")
            )
            st.rerun()