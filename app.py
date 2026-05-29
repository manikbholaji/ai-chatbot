import streamlit as st
import json
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from chatbot import get_local_response, SYSTEM_PROMPT
from puter_bridge import puter_bridge
import uuid
import hashlib

BASE_DIR = Path(__file__).resolve().parent

def project_path(*parts):
    return BASE_DIR.joinpath(*parts)

# Page configuration
st.set_page_config(page_title="CU AI Advisor", layout="wide", page_icon="🎓")

# Professional UI Styling (Clean & Modern)
st.markdown("""
    <style>
    /* Main Layout */
    .block-container { padding-top: 2rem !important; padding-bottom: 0rem !important; }
    .main { background-color: #fcfcfc; }
    
    /* Typography & Buttons */
    h1, h2, h3 { color: #1e1e1e; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton > button { border-radius: 8px; font-weight: 500; transition: all 0.2s ease; }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    /* Chat Aesthetics */
    .stChatMessage { border-radius: 12px; margin-bottom: 0.5rem !important; }
    .stChatFloatingInputContainer { padding-bottom: 30px; }
    
    /* Sidebar Polish */
    section[data-testid="stSidebar"] { background-color: #f1f3f6; }
    .sidebar-content { padding: 1.5rem; }
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

# Interaction Logging
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

def load_recent_history(username, limit=10):
    log_f = project_path("data", "interaction_logs.jsonl")
    if not os.path.exists(log_f):
        return []
    
    user_messages = []
    with open(log_f, "r") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("user") == username:
                user_messages.append({"role": "user", "content": entry["student_message"]})
                user_messages.append({"role": "assistant", "content": entry["bot_response"]})
    
    return user_messages[-limit:]

# --- LOCAL USER DATABASE SYSTEM ---
USERS_FILE = project_path("data", "users.json")

def init_db():
    os.makedirs(USERS_FILE.parent, exist_ok=True)
    if not USERS_FILE.exists():
        with open(USERS_FILE, "w") as f:
            # Pre-register Admin
            admin_hash = hashlib.sha256("Manik".encode()).hexdigest()
            json.dump({"Manik": {"password": admin_hash, "role": "admin"}}, f)

def load_users():
    init_db()
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Username exists"
    users[username] = {
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "role": "student"
    }
    save_users(users)
    return True, "Account created!"

def authenticate(username, password):
    users = load_users()
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    user_data = users.get(username)
    if user_data and user_data.get("password") == pw_hash:
        return True, user_data.get("role", "student")
    return False, None

# --- SIDEBAR: AUTH & NAVIGATION ---
st.sidebar.title("🎓 CU Advisor")

with st.sidebar:
    st.markdown("### 🔐 User Account")
    
    if st.session_state.authenticated:
        st.success(f"Welcome, **{st.session_state.user['name']}**")
        st.caption(f"Role: {st.session_state.user['role'].title()}")
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()
    else:
        auth_tab1, auth_tab2 = st.tabs(["Login", "Sign Up"])
        
        with auth_tab1:
            with st.form("login_form"):
                u_in = st.text_input("Username")
                p_in = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    success, role = authenticate(u_in, p_in)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = {"name": u_in, "role": role}
                        # Start with a clean session for Student Advisor as requested
                        st.session_state.messages = []
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        
        with auth_tab2:
            with st.form("signup_form"):
                new_u = st.text_input("New Username")
                new_p = st.text_input("New Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if len(new_u) < 3 or len(new_p) < 4:
                        st.warning("Too short!")
                    else:
                        ok, msg = register_user(new_u, new_p)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

    st.caption("✅ Mode: " + ("Personalized" if st.session_state.authenticated else "Anonymous"))

st.sidebar.markdown("---")

# Navigation Menu
pages = ["Student Advisor", "Chat History"]
if st.session_state.authenticated and st.session_state.user.get('role') == 'admin':
    pages.append("Admin Dashboard")

if "page" not in st.session_state:
    st.session_state.page = "Student Advisor"
if st.session_state.page not in pages:
    st.session_state.page = "Student Advisor"

nav_page = st.sidebar.radio("Navigation", pages, index=pages.index(st.session_state.page))
st.session_state.page = nav_page

# Keyless AI Driver
ai_driver = puter_bridge(key="headless_ai_driver")

# --- PAGE: STUDENT ADVISOR ---
if st.session_state.page == "Student Advisor":
    st.title("🎓 Chandigarh University Advisor")
    
    # FAQ & Quick Actions Section (Always visible at the top if no messages yet)
    if not st.session_state.messages:
        st.markdown("#### How can I assist you today? 🚀")
        st.caption("Select a common query or type your own below.")
        
        faq_col1, faq_col2 = st.columns(2)
        
        with faq_col1:
            if st.button("📚 What courses are offered?", use_container_width=True):
                prompt = "What courses are offered at Chandigarh University?"
                st.session_state.messages.append({"role": "user", "content": prompt})
                local = get_local_response(prompt)
                if local:
                    st.session_state.messages.append({"role": "assistant", "content": local})
                    log_interaction(prompt, local, TextBlob(prompt).sentiment.polarity, "FAQ-QuickAction")
                st.rerun()
            if st.button("🗓️ How do I book an appointment?", use_container_width=True):
                prompt = "How do I book an academic advising appointment?"
                st.session_state.messages.append({"role": "user", "content": prompt})
                local = get_local_response(prompt)
                if local:
                    st.session_state.messages.append({"role": "assistant", "content": local})
                    log_interaction(prompt, local, TextBlob(prompt).sentiment.polarity, "FAQ-QuickAction")
                st.rerun()
        
        with faq_col2:
            if st.button("⚖️ What is the attendance policy?", use_container_width=True):
                prompt = "Tell me about the university attendance policy."
                st.session_state.messages.append({"role": "user", "content": prompt})
                local = get_local_response(prompt)
                if local:
                    st.session_state.messages.append({"role": "assistant", "content": local})
                    log_interaction(prompt, local, TextBlob(prompt).sentiment.polarity, "FAQ-QuickAction")
                st.rerun()
            if st.button("🤔 How do you recommend courses?", use_container_width=True):
                prompt = "What is your logic behind recommending courses?"
                st.session_state.messages.append({"role": "user", "content": prompt})
                local = get_local_response(prompt)
                if local:
                    st.session_state.messages.append({"role": "assistant", "content": local})
                    log_interaction(prompt, local, TextBlob(prompt).sentiment.polarity, "FAQ-QuickAction")
                st.rerun()
        
        st.divider()

    # Chat Container
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # AI Processing State
    if st.session_state.processing:
        with st.chat_message("assistant"):
            st.info("Thinking... 🧠")
            
            # Construct context-aware history for professional tracking
            sys_content = SYSTEM_PROMPT
            if st.session_state.authenticated:
                sys_content += f"\n\nCURRENT USER CONTEXT: You are helping {st.session_state.user['name']} ({st.session_state.user['role']})."
            
            history = [{"role": "system", "content": sys_content}]
            for m in st.session_state.messages:
                history.append({"role": m["role"], "content": m["content"]})
            
            result = puter_bridge(
                messages=history,
                command="anonymous_chat",
                request_id=st.session_state.last_req_id,
                key=f"ai_call_{st.session_state.last_req_id}"
            )
            
            if result and result.get('type') == 'ai_response':
                if result.get('status') == 'success':
                    resp = result.get('message', {}).get('content', "No response")
                    st.session_state.messages.append({"role": "assistant", "content": resp})
                    user_msg = st.session_state.messages[-2]["content"]
                    sentiment_score = TextBlob(user_msg).sentiment.polarity
                    log_interaction(user_msg, resp, sentiment_score, "AI-Client")
                    st.session_state.processing = False
                    st.session_state.last_req_id = str(uuid.uuid4())
                    st.rerun()
                elif result.get('status') == 'error':
                    st.error("I'm having trouble connecting to my brain right now. Please try again or ask about courses/policies which I can answer instantly!")
                    st.session_state.processing = False
                    if st.button("Retry"):
                        st.rerun()

    # Input Logic
    if not st.session_state.processing:
        if prompt := st.chat_input("How can I help you today?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            local = get_local_response(prompt)
            if local:
                st.session_state.messages.append({"role": "assistant", "content": local})
                log_interaction(prompt, local, TextBlob(prompt).sentiment.polarity, "Local-Logic")
                st.rerun()
            else:
                st.session_state.processing = True
                st.session_state.last_req_id = str(uuid.uuid4())
                st.rerun()

# --- PAGE: CHAT HISTORY ---
elif st.session_state.page == "Chat History":
    st.title("📜 Conversation Logs")
    
    if not st.session_state.authenticated:
        st.warning("💡 Sign in via sidebar to access your persistent, professionally organized history.")
        if st.session_state.messages:
            st.subheader("Current Session")
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
    else:
        u_name = st.session_state.user['name']
        log_f = project_path("data", "interaction_logs.jsonl")
        
        if os.path.exists(log_f):
            logs = []
            with open(log_f, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get("user") == u_name:
                        logs.append(entry)
            
            if logs:
                df = pd.DataFrame(logs)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                df = df.sort_values('timestamp', ascending=False)
                
                for d in df['date'].unique():
                    with st.expander(f"📅 {d.strftime('%d %b %Y')}", expanded=True):
                        d_logs = df[df['date'] == d].sort_values('timestamp', ascending=True)
                        for _, r in d_logs.iterrows():
                            c1, c2 = st.columns([1, 10])
                            c1.caption(r['timestamp'].strftime('%H:%M'))
                            with st.chat_message("user"):
                                st.write(r['student_message'])
                            with st.chat_message("assistant"):
                                st.write(r['bot_response'])
            else:
                st.info("No recorded logs for this name.")
        else:
            st.info("Database empty.")

# --- PAGE: ADMIN DASHBOARD ---
elif st.session_state.page == "Admin Dashboard":
    st.title("📊 Advisor Analytics")
    
    log_f = project_path("data", "interaction_logs.jsonl")
    if os.path.exists(log_f):
        with open(log_f, "r") as f:
            logs = [json.loads(line) for line in f]
        df = pd.DataFrame(logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        m1, m2 = st.columns(2)
        m1.metric("Total Queries", len(df))
        m2.metric("Avg Sentiment", round(df['sentiment'].mean(), 2))
        
        st.subheader("Sentiment Analysis")
        def categorize_sentiment(score):
            if score > 0.1: return "Decisive / Satisfied (Positive)"
            elif score < -0.1: return "Frustrated / Anxious (Negative)"
            else: return "Uncertain / Hesitant (Neutral)"
            
        df['sentiment_label'] = df['sentiment'].apply(categorize_sentiment)
        sentiment_counts = df['sentiment_label'].value_counts().reset_index()
        
        fig = px.pie(sentiment_counts, values='count', names='sentiment_label', hole=0.4,
                     color='sentiment_label',
                     color_discrete_map={
                         "Decisive / Satisfied (Positive)": "#2ecc71",
                         "Uncertain / Hesitant (Neutral)": "#f1c40f",
                         "Frustrated / Anxious (Negative)": "#e74c3c"
                     })
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Recent Activity")
        st.dataframe(df[['timestamp', 'user', 'mode', 'sentiment_label', 'student_message', 'bot_response']], use_container_width=True)
    else:
        st.info("No logs collected yet.")

# --- PAGE: APPOINTMENT MANAGEMENT ---
elif st.session_state.page == "Appointment Management":
    st.title("📅 Appointment Management")
    st.markdown("Professional oversight of all academic advising schedules.")
    
    appt_f = project_path("data", "appointments.json")
    if os.path.exists(appt_f):
        with open(appt_f, "r") as f:
            appts = json.load(f)
        
        if appts:
            df = pd.DataFrame(appts)
            # Ensure proper typing for sorting
            df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
            df = df.sort_values('datetime', ascending=True)
            
            # KPI Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Appointments", len(df))
            upcoming = len(df[df['datetime'] >= pd.Timestamp.now()])
            m2.metric("Upcoming Sessions", upcoming)
            m3.metric("Unique Students", df['student_name'].nunique())
            
            st.divider()
            
            # Beautiful Calendar-style View
            st.subheader("📅 Scheduled Sessions")
            
            # Group by Date for better organization
            for date, group in df.groupby('date'):
                with st.expander(f"🗓️ {pd.to_datetime(date).strftime('%A, %d %B %Y')}", expanded=True):
                    for _, row in group.iterrows():
                        with st.container():
                            c1, c2, c3 = st.columns([1, 3, 2])
                            with c1:
                                st.markdown(f"### {row['time']}")
                            with c2:
                                st.markdown(f"**Student:** {row['student_name']}")
                                st.caption(f"**Query/Topic:** {row['course_name']}")
                            with c3:
                                st.info(f"Booked on: {pd.to_datetime(row['timestamp']).strftime('%Y-%m-%d')}")
                            st.divider()
            
            # Data Export Option
            st.download_button(
                label="📥 Export Schedule (CSV)",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"cu_appointments_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.info("No appointments have been booked yet.")
    else:
        st.info("Appointment database not found.")

st.sidebar.markdown("---")
st.sidebar.caption("MCA Final Project | Serverless AI Architecture")
