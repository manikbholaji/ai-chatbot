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
import time

BASE_DIR = Path(__file__).resolve().parent

def project_path(*parts):
    return BASE_DIR.joinpath(*parts)

# Page configuration
st.set_page_config(page_title="AI chatbot", layout="wide", page_icon="🤖")

# Custom CSS
st.markdown("""
    <style>
    /* Spacing Fixes */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    .stChatFloatingInputContainer { padding-bottom: 20px; }
    div[data-testid="stVerticalBlock"] > div { margin-top: -0.5rem; }
    .stChatMessage { margin-bottom: -1rem !important; }
    
    /* UI Refinements */
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

# 1. Puter Authentication & AI Driver
with st.sidebar:
    st.markdown("### 🔐 User Account")
    
    # The bridge handles Google Login and serves as our AI Driver
    bridge_result = puter_bridge(key="main_auth_bridge")
    
    if bridge_result:
        if bridge_result.get('type') == 'auth' and bridge_result.get('status') == 'success':
            st.session_state.authenticated = True
            st.session_state.user = bridge_result.get('user')
        elif bridge_result.get('type') == 'auth_cleared':
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()

    if st.session_state.authenticated:
        st.info(f"✅ AI Mode: Enabled ({st.session_state.user['name']})")
    else:
        st.success("✅ Client-Side AI: Enabled (Anonymous)")

st.sidebar.markdown("---")
# Use session state to control the radio button
if "page" not in st.session_state:
    st.session_state.page = "Student Advisor"

pages = ["Student Advisor", "Chat History", "Admin Dashboard"]
page = st.sidebar.radio("Go to", pages, index=pages.index(st.session_state.page), key="sidebar_nav")
st.session_state.page = page

if page == "Student Advisor":
    st.title("🎓 Chandigarh University Academic Advisor")
    
    if not st.session_state.authenticated:
        st.markdown("""
            ### Welcome to the Smart Academic Advisor! 🚀
            
            I am here to help you navigate your academic journey at **Chandigarh University**. 
            
            **What I can do for you:**
            - 📚 **Course Recommendations:** Find the best B.Tech, MCA, or MBA programs based on your interests.
            - 🗓️ **Advising Appointments:** Book a session with a real counselor.
            - 🤖 **Unlimited Anonymous AI:** Get instant answers to complex questions, powered by Puter.js (No login required!).
            
            ---
            #### 🔒 Personalized Mode
            **Sign in with Google** in the sidebar to unlock your name in reports and advanced advising.
        """)
        st.divider()

    # Display chat history (Static & Stable)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Processing indicator
    if st.session_state.processing:
        with st.chat_message("assistant"):
            st.write("Consulting AI Advisor for complex query... 🧠")
            
            # HEADLESS AI CALL via Puter Bridge
            history_context = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                history_context.append({"role": m["role"], "content": m["content"]})
            
            ai_bridge = puter_bridge(
                messages=history_context,
                command="anonymous_chat",
                request_id=st.session_state.last_req_id,
                key=f"ai_driver_{st.session_state.last_req_id}"
            )
            
            if ai_bridge and ai_bridge.get('type') == 'ai_response':
                if ai_bridge.get('status') == 'success':
                    response_text = ai_bridge.get('message', {}).get('content', "No response")
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    log_interaction(st.session_state.messages[-2]["content"], response_text, 0, "Puter-Client")
                    st.session_state.processing = False
                    st.session_state.last_req_id = str(uuid.uuid4())
                    st.rerun()
                elif ai_bridge.get('status') == 'error':
                    st.error(f"AI Connection issue: {ai_bridge.get('error')}")
                    st.session_state.processing = False

    # Chat input
    if not st.session_state.processing:
        if prompt := st.chat_input("Ask about courses, attendance, or book an appointment..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # STEP 1: Always try local lookup first (Accurate & Precise)
            local_resp = get_local_response(prompt)
            
            if local_resp:
                st.session_state.messages.append({"role": "assistant", "content": local_resp})
                log_interaction(prompt, local_resp, TextBlob(prompt).sentiment.polarity, "Local-Logic")
                st.rerun()
            else:
                # STEP 2: Logic didn't fit. Trigger Client-Side AI via bridge.
                st.session_state.processing = True
                st.session_state.last_req_id = str(uuid.uuid4())
                st.rerun()

elif page == "Chat History":
    st.title("📜 Your Chat History")
    
    if not st.session_state.authenticated:
        st.warning("💡 **Sign in with Google** in the sidebar to unlock your persistent, personalized chat history!")
        
        if st.session_state.messages:
            st.subheader("Current Session History")
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        else:
            st.info("No active conversation in this session.")
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
                            with cols[0]:
                                st.caption(row['timestamp'].strftime('%H:%M'))
                            with st.chat_message("user"):
                                st.write(row['student_message'])
                            with st.chat_message("assistant"):
                                st.write(row['bot_response'])
                            st.divider()
            else:
                st.info("Your chat history is empty. Start a conversation in the 'Student Advisor' tab!")
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
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Interactions", len(df))
        col2.metric("Avg Sentiment Score", round(df['sentiment'].mean(), 2))
        
        st.subheader("Mode Distribution (Local vs AI)")
        mode_counts = df['mode'].value_counts().reset_index()
        fig_mode = px.pie(mode_counts, values='count', names='mode', title='How Queries are Resolved')
        st.plotly_chart(fig_mode, use_container_width=True)
        
        st.subheader("Interaction Logs")
        st.dataframe(df[['timestamp', 'user', 'mode', 'student_message', 'bot_response']])
    else:
        st.info("No interaction logs found yet.")

st.sidebar.markdown("---")
st.sidebar.info("MCA Final Semester Project | Smart Hybrid AI")
