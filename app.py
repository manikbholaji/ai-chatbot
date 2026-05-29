import streamlit as st
import json
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from chatbot import get_local_response, book_appointment, SYSTEM_PROMPT
from puter_bridge import puter_bridge
import uuid
import hashlib

BASE_DIR = Path(__file__).resolve().parent

def project_path(*parts):
    return BASE_DIR.joinpath(*parts)

# Page configuration
st.set_page_config(page_title="AI chatbot", layout="wide", page_icon="🤖")

# Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    .stChatFloatingInputContainer { padding-bottom: 20px; }
    div[data-testid="stVerticalBlock"] > div { margin-top: -0.5rem; }
    .stChatMessage { margin-bottom: -1rem !important; }
    .main { background-color: #f8f9fa; }
    .stButton > button { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "last_req_id" not in st.session_state:
    st.session_state.last_req_id = str(uuid.uuid4())

# --- SHARED ANALYTICS LOGGING ---
def log_interaction(message, response, sentiment, mode):
    log_file = project_path("data", "interaction_logs.jsonl")
    log_entry = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "user": st.session_state.user['name'] if st.session_state.user else "Anonymous",
        "mode": mode,
        "student_message": message,
        "bot_response": response,
        "sentiment": sentiment
    }
    os.makedirs(log_file.parent, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# Sidebar Navigation
st.sidebar.title("🤖 AI chatbot")

# --- CUSTOM AUTHENTICATION MODULE ---
with st.sidebar:
    st.markdown("### 🔐 User Personalization")
    
    if st.session_state.authenticated:
        st.success(f"Personalized as: **{st.session_state.user['name']}**")
        if st.button("Change User / Sign Out"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()
    else:
        with st.expander("Enable Personalized Mode", expanded=True):
            user_name = st.text_input("Enter your name", placeholder="Student Name...")
            is_admin = st.checkbox("Admin Access")
            admin_pass = ""
            if is_admin:
                admin_pass = st.text_input("Admin Password", type="password")
            
            if st.button("Get Started"):
                if is_admin:
                    # Admin Validation (Manik / Manik)
                    if user_name == "Manik" and admin_pass == "Manik":
                        st.session_state.authenticated = True
                        st.session_state.user = {"name": "Manik", "role": "admin"}
                        st.success("Admin Access Granted!")
                        st.rerun()
                    else:
                        st.error("Invalid Admin Credentials")
                elif user_name.strip():
                    st.session_state.authenticated = True
                    st.session_state.user = {"name": user_name.strip(), "role": "student"}
                    st.success(f"Welcome, {user_name}!")
                    st.rerun()
                else:
                    st.error("Please enter a name")

    if st.session_state.authenticated:
        st.info("✅ Personalized Mode: Active")
    else:
        st.warning("✅ Anonymous Mode: Active")

st.sidebar.markdown("---")

# Use session state to control the radio button
if "page" not in st.session_state:
    st.session_state.page = "Student Advisor"

# Pages visible to everyone
pages = ["Student Advisor", "Chat History"]

# Admin Only Page
if st.session_state.authenticated and st.session_state.user.get('role') == 'admin':
    pages.append("Admin Dashboard")

# Ensure the current page is still in the allowed list
if st.session_state.page not in pages:
    st.session_state.page = "Student Advisor"

page = st.sidebar.radio("Go to", pages, index=pages.index(st.session_state.page), key="sidebar_nav")
st.session_state.page = page

# Headless AI Driver (Always runs in background to handle requests)
# This is our keyless, anonymous, client-side driver
ai_driver = puter_bridge(key="headless_ai_driver")

if page == "Student Advisor":
    st.title("🎓 Chandigarh University Academic Advisor")
    
    if not st.session_state.authenticated:
        st.markdown("""
            ### Welcome to the Smart Academic Advisor! 🚀
            I am here to help you navigate your academic journey at **Chandigarh University**. 
            
            **What I can do for you:**
            - 📚 **Course Recommendations**
            - 🗓️ **Advising Appointments**
            - 🤖 **Unlimited Anonymous AI** (No login required!)
        """)
        st.divider()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Processing indicator & Headless Call logic
    if st.session_state.processing:
        with st.chat_message("assistant"):
            st.write("Consulting AI Advisor... 🧠")
            
            # Prepare messages
            history_context = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                history_context.append({"role": m["role"], "content": m["content"]})
            
            # Trigger Headless AI Call
            result = puter_bridge(
                messages=history_context,
                command="anonymous_chat",
                request_id=st.session_state.last_req_id,
                key=f"ai_call_{st.session_state.last_req_id}"
            )
            
            if result and result.get('type') == 'ai_response':
                if result.get('status') == 'success':
                    response_text = result.get('message', {}).get('content', "No response")
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    log_interaction(st.session_state.messages[-2]["content"], response_text, 0, "Puter-Client")
                    st.session_state.processing = False
                    st.session_state.last_req_id = str(uuid.uuid4())
                    st.rerun()
                elif result.get('status') == 'error':
                    st.error(f"AI Connection issue: {result.get('error')}")
                    st.session_state.processing = False

    # Chat input
    if not st.session_state.processing:
        if prompt := st.chat_input("Ask about courses, attendance, or book an appointment..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            local_resp = get_local_response(prompt)
            if local_resp:
                st.session_state.messages.append({"role": "assistant", "content": local_resp})
                log_interaction(prompt, local_resp, TextBlob(prompt).sentiment.polarity, "Local-Logic")
                st.rerun()
            else:
                st.session_state.processing = True
                st.session_state.last_req_id = str(uuid.uuid4())
                st.rerun()

elif page == "Chat History":
    st.title("📜 Your Chat History")
    
    if not st.session_state.authenticated:
        st.warning("💡 **Enable Personalized Mode** in the sidebar to unlock your chat history!")
        if st.session_state.messages:
            st.subheader("Current Session History")
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
    else:
        current_user = st.session_state.user['name']
        log_file = project_path("data", "interaction_logs.jsonl")
        
        if os.path.exists(log_file):
            user_logs = []
            with open(log_file, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get("user") == current_user:
                        user_logs.append(entry)
            
            if user_logs:
                df = pd.DataFrame(user_logs)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                df = df.sort_values('timestamp', ascending=False)
                dates = df['date'].unique()
                
                st.write(f"Showing chat history for **{current_user}**")
                for date in dates:
                    with st.expander(f"📅 {date.strftime('%B %d, %Y')}", expanded=(date == dates[0])):
                        day_logs = df[df['date'] == date].sort_values('timestamp', ascending=True)
                        for _, row in day_logs.iterrows():
                            cols = st.columns([1, 11])
                            with cols[0]: st.caption(row['timestamp'].strftime('%H:%M'))
                            with st.chat_message("user"): st.write(row['student_message'])
                            with st.chat_message("assistant"): st.write(row['bot_response'])
                            st.divider()
            else:
                st.info("No history found for your name.")
        else:
            st.info("No interaction records found.")

elif page == "Admin Dashboard":
    st.title("📊 Student Interaction Analytics")
    
    log_file = project_path("data", "interaction_logs.jsonl")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = [json.loads(line) for line in f]
        df = pd.DataFrame(logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        col1, col2 = st.columns(2)
        col1.metric("Total Interactions", len(df))
        col2.metric("Avg Sentiment", round(df['sentiment'].mean(), 2))
        
        st.subheader("Query Resolution Modes")
        mode_counts = df['mode'].value_counts().reset_index()
        fig_mode = px.pie(mode_counts, values='count', names='mode', title='Local vs AI Logic')
        st.plotly_chart(fig_mode, use_container_width=True)
        
        st.subheader("Interaction Logs")
        st.dataframe(df[['timestamp', 'user', 'mode', 'student_message', 'bot_response']])
    else:
        st.info("No logs found.")

st.sidebar.markdown("---")
st.sidebar.info("MCA Final Project | 100% Client-Side AI")
