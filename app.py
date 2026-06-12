
import streamlit as st
from pathlib import Path
import pandas as pd
from textblob import TextBlob
from chatbot import get_local_response, SYSTEM_PROMPT, book_appointment
from puter_bridge import puter_bridge
from database import (
    authenticate_user, add_user, log_interaction_db, 
    get_user_history, get_all_logs, get_appointments_db
)
import uuid
import hashlib

BASE_DIR = Path(__file__).resolve().parent

# Interaction Logging (SQLite)
def log_interaction(message, response, sentiment, mode):
    user_name = st.session_state.user['name'] if st.session_state.user else "Anonymous"
    log_interaction_db(user_name, mode, message, response, sentiment)
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

def load_recent_history(username, limit=10):
    return get_user_history(username, limit)

# --- USER AUTHENTICATION (SQLite) ---
def register_user(username, password):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    return add_user(username, pw_hash)

def authenticate(username, password):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    role = authenticate_user(username, pw_hash)
    if role:
        return True, role
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
if st.session_state.authenticated:
    pages.append("Book Appointment")
if st.session_state.authenticated and st.session_state.user.get('role') == 'admin':
    pages.append("Admin Dashboard")
    pages.append("Appointment Management")

if "page" not in st.session_state:
    st.session_state.page = "Student Advisor"
if st.session_state.page not in pages:
    st.session_state.page = "Student Advisor"

nav_page = st.sidebar.radio("Navigation", pages, index=pages.index(st.session_state.page))
st.session_state.page = nav_page

# --- PAGE: STUDENT ADVISOR ---
if st.session_state.page == "Student Advisor":
    st.title("🎓 Chandigarh University Advisor")
    
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

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.processing:
        with st.chat_message("assistant"):
            st.info("Thinking... 🧠")
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
                    st.error("I'm having trouble connecting to my brain right now. Please try again or ask about courses/policies!")
                    st.session_state.processing = False
                    if st.button("Retry"):
                        st.rerun()

    prompt = st.chat_input("How can I help you today?", disabled=st.session_state.processing)
    if prompt and not st.session_state.processing:
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

# --- PAGE: BOOK APPOINTMENT ---
elif st.session_state.page == "Book Appointment":
    st.title("📅 Book Academic Advising Appointment")
    st.write("Schedule a session with an academic advisor to discuss your course options.")
    
    with st.form("book_appt_form"):
        st.write("### Appointment Details")
        appt_date = st.date_input("Select Date")
        appt_time = st.time_input("Select Time")
        course_topic = st.text_input("Topic/Course of Interest", placeholder="e.g. Master of Computer Applications")
        
        if st.form_submit_button("Book Appointment"):
            if not course_topic:
                st.error("Please enter a topic or course of interest.")
            else:
                date_str = appt_date.strftime("%Y-%m-%d")
                time_str = appt_time.strftime("%H:%M")
                student_name = st.session_state.user['name']
                
                result_msg = book_appointment(date_str, time_str, student_name, course_topic)
                if result_msg.startswith("Success"):
                    st.success(result_msg)
                    st.balloons()
                else:
                    st.error(result_msg)

# --- PAGE: CHAT HISTORY ---
elif st.session_state.page == "Chat History":
    st.title("📜 Conversation Logs")
    if not st.session_state.authenticated:
        st.warning("💡 Sign in via sidebar to access your persistent, professionally organized history.")
    else:
        u_name = st.session_state.user['name']
        history = get_user_history(u_name, limit=50)
        if history:
            for i in range(0, len(history), 2):
                with st.chat_message("user"): 
                    st.write(history[i]['content'])
                with st.chat_message("assistant"): 
                    st.write(history[i+1]['content'])
                st.divider()
        else:
            st.info("No recorded logs for this name.")

# --- PAGE: ADMIN DASHBOARD ---
elif st.session_state.page == "Admin Dashboard":
    st.title("📊 Advisor Analytics")
    logs = get_all_logs()
    if logs:
        df = pd.DataFrame(logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        m1, m2 = st.columns(2)
        m1.metric("Total Queries", len(df))
        m2.metric("Avg Sentiment", round(df['sentiment'].mean(), 2))
        st.subheader("Recent Activity")
        st.dataframe(df[['timestamp', 'user', 'mode', 'student_message', 'bot_response']], use_container_width=True)
    else:
        st.info("No logs collected yet.")

# --- PAGE: APPOINTMENT MANAGEMENT ---
elif st.session_state.page == "Appointment Management":
    st.title("📅 Appointment Management")
    appts = get_appointments_db()
    if appts:
        df = pd.DataFrame(appts)
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df = df.sort_values('datetime', ascending=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Appointments", len(df))
        m2.metric("Upcoming Sessions", len(df[df['datetime'] >= pd.Timestamp.now()]))
        m3.metric("Unique Students", df['student_name'].nunique())
        st.subheader("📅 Scheduled Sessions")
        for date, group in df.groupby('date'):
            with st.expander(f"🗓️ {pd.to_datetime(date).strftime('%A, %d %B %Y')}", expanded=True):
                for _, row in group.iterrows():
                    c1, c2, c3 = st.columns([1, 3, 2])
                    c1.markdown(f"### {row['time']}")
                    c2.markdown(f"**Student:** {row['student_name']}\n**Topic:** {row['course_name']}")
                    c3.info(f"Booked: {pd.to_datetime(row['timestamp']).strftime('%Y-%m-%d')}")
                    st.divider()
    else:
        st.info("No appointments found.")

st.sidebar.markdown("---")
st.sidebar.caption("MCA Final Project | Serverless AI Architecture")
