
import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from chatbot import get_local_response, SYSTEM_PROMPT, book_appointment, get_ai_response
from database import (
    authenticate_user, add_user, log_interaction_db, 
    get_user_history, get_all_logs, get_appointments_db,
    is_production_db, get_db_error
)
import uuid
import hashlib

BASE_DIR = Path(__file__).resolve().parent

# Interaction Logging (SQLite)
def log_interaction(message, response, sentiment, mode):
    user_name = st.session_state.user['name'] if st.session_state.user else "Anonymous"
    log_interaction_db(user_name, mode, message, response, sentiment)

st.set_page_config(page_title="CU AI Advisor", layout="wide", page_icon="🎓")

# Professional UI Styling (Refined for MCA Project)
st.markdown("""
    <style>
    /* Main Layout */
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    .main { background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%); }
    
    /* Typography & Buttons */
    h1, h2, h3 { color: #1e1e1e; font-family: 'Inter', 'Segoe UI', sans-serif; font-weight: 700; }
    .stButton > button { 
        border-radius: 10px; 
        font-weight: 600; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid #e0e0e0;
    }
    .stButton > button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        border-color: #4285F4;
    }
    
    /* Chat Aesthetics */
    .stChatMessage { border-radius: 15px; border: 1px solid #f0f0f0; margin-bottom: 0.8rem !important; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .stChatFloatingInputContainer { padding-bottom: 40px; }
    
    /* Sidebar Polish */
    section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #eee; }
    .sidebar-content { padding: 2rem; }
    
    /* Custom Components */
    div[data-testid="stMetric"] {
        background: white;
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #eee;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
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
    st.markdown("### 🔐 Account")
    
    if st.session_state.authenticated:
        st.success(f"**{st.session_state.user['name']}**")
        st.caption(f"Role: {st.session_state.user['role'].upper()}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Logout", width="stretch"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("🗑️ Clear", width="stretch", help="Clear current chat context"):
                st.session_state.messages = []
                st.rerun()
    else:
        auth_tab1, auth_tab2 = st.tabs(["Login", "Sign Up"])
        
        with auth_tab1:
            with st.form("login_form"):
                u_in = st.text_input("Username")
                p_in = st.text_input("Password", type="password")
                if st.form_submit_button("Login", width="stretch"):
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
                if st.form_submit_button("Create Account", width="stretch"):
                    if len(new_u) < 3 or len(new_p) < 4:
                        st.warning("Too short!")
                    else:
                        ok, msg = register_user(new_u, new_p)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
    
    if not st.session_state.authenticated:
        if st.button("🗑️ Clear Chat", width="stretch"):
            st.session_state.messages = []
            st.rerun()

    st.caption("✅ Mode: " + ("Personalized" if st.session_state.authenticated else "Anonymous"))
    
    # Render DB Status Badge
    db_status = "Production (Aiven)" if is_production_db() else "Local Fallback (SQLite)"
    db_icon = "🟢" if is_production_db() else "🟡"
    db_err = get_db_error()
    if db_err and not is_production_db():
        st.caption(f"{db_icon} Database: {db_status}", help=f"Diagnostics: {db_err}")
    else:
        st.caption(f"{db_icon} Database: {db_status}")

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
            if st.button("📚 What courses are offered?", width="stretch"):
                prompt = "What courses are offered at Chandigarh University?"
                st.session_state.messages.append({"role": "user", "content": prompt})
                local = get_local_response(prompt)
                if local:
                    st.session_state.messages.append({"role": "assistant", "content": local})
                    log_interaction(prompt, local, TextBlob(prompt).sentiment.polarity, "FAQ-QuickAction")
                st.rerun()
            if st.button("🗓️ How do I book an appointment?", width="stretch"):
                prompt = "How do I book an academic advising appointment?"
                st.session_state.messages.append({"role": "user", "content": prompt})
                local = get_local_response(prompt)
                if local:
                    st.session_state.messages.append({"role": "assistant", "content": local})
                    log_interaction(prompt, local, TextBlob(prompt).sentiment.polarity, "FAQ-QuickAction")
                st.rerun()
        
        with faq_col2:
            if st.button("⚖️ What is the attendance policy?", width="stretch"):
                prompt = "Tell me about the university attendance policy."
                st.session_state.messages.append({"role": "user", "content": prompt})
                local = get_local_response(prompt)
                if local:
                    st.session_state.messages.append({"role": "assistant", "content": local})
                    log_interaction(prompt, local, TextBlob(prompt).sentiment.polarity, "FAQ-QuickAction")
                st.rerun()
            if st.button("🤔 How do you recommend courses?", width="stretch"):
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

    prompt = st.chat_input("How can I help you today?")
    if prompt:
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        local = get_local_response(prompt)
        if local:
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(local)
            st.session_state.messages.append({"role": "assistant", "content": local})
            log_interaction(prompt, local, TextBlob(prompt).sentiment.polarity, "Local-Logic")
            st.rerun()
        else:
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking... 🧠"):
                        sys_content = SYSTEM_PROMPT
                        if st.session_state.authenticated:
                            sys_content += f"\n\nCURRENT USER CONTEXT: You are helping {st.session_state.user['name']} ({st.session_state.user['role']})."
                        
                        history = [{"role": "system", "content": sys_content}]
                        for m in st.session_state.messages:
                            history.append({"role": m["role"], "content": m["content"]})
                        
                        result = get_ai_response(history)
                        if result and result.get('status') == 'success':
                            resp = result.get('content', "No response")
                            st.markdown(resp)
                            st.session_state.messages.append({"role": "assistant", "content": resp})
                            log_interaction(prompt, resp, TextBlob(prompt).sentiment.polarity, "AI-Client")
                            st.rerun()
                        else:
                            err_msg = result.get('message', 'Unknown error') if result else 'Unknown error'
                            fallback_msg = (
                                f"I am currently operating in Local offline mode (diagnostics: {err_msg}). "
                                "I can still assist you with course information and academic policies. "
                                "For example, try asking: 'What courses are offered?' or 'What is the attendance policy?'"
                            )
                            st.markdown(fallback_msg)
                            st.session_state.messages.append({"role": "assistant", "content": fallback_msg})
                            log_interaction(prompt, fallback_msg, 0.0, "System-Fallback")
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
            for msg in history:
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])
        else:
            st.info("No recorded logs for this name.")

# --- PAGE: ADMIN DASHBOARD ---
elif st.session_state.page == "Admin Dashboard":
    st.title("📊 Advisor Analytics")
    logs = get_all_logs()
    if logs:
        df = pd.DataFrame(logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
        
        # Top Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Queries", len(df))
        m2.metric("Avg Sentiment", round(df['sentiment'].mean(), 2))
        m3.metric("Active Users", df['user'].nunique())
        
        st.divider()
        
        # Charts Row
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("📈 Query Volume Over Time")
            df_daily = df.set_index('timestamp').resample('D').count().reset_index()
            fig_vol = px.line(df_daily, x='timestamp', y='student_message', labels={'student_message': 'Queries'},
                              template="plotly_white", color_discrete_sequence=['#4285F4'])
            st.plotly_chart(fig_vol, width="stretch")
            
        with c2:
            st.subheader("😊 Sentiment Distribution")
            def classify_sentiment(score):
                if score > 0.05:
                    return "Positive"
                elif score < -0.05:
                    return "Negative"
                else:
                    return "Neutral"
            
            df['sentiment_category'] = df['sentiment'].apply(classify_sentiment)
            counts = df['sentiment_category'].value_counts()
            total = len(df)
            cats = ["Positive", "Neutral", "Negative"]
            counts_dict = {cat: counts.get(cat, 0) for cat in cats}
            pcts = {cat: (counts_dict[cat] / total * 100) if total > 0 else 0.0 for cat in cats}
            
            plot_df = pd.DataFrame([
                {"Sentiment": f"Positive ({int(round(pcts['Positive']))}%)", "Percentage": pcts['Positive'], "Category": "Positive"},
                {"Sentiment": f"Neutral ({int(round(pcts['Neutral']))}%)", "Percentage": pcts['Neutral'], "Category": "Neutral"},
                {"Sentiment": f"Negative ({int(round(pcts['Negative']))}%)", "Percentage": pcts['Negative'], "Category": "Negative"}
            ])
            
            fig_sent = px.bar(
                plot_df, 
                x='Percentage', 
                y='Sentiment', 
                orientation='h',
                color='Category',
                color_discrete_map={
                    'Positive': '#34A853',
                    'Neutral': '#FBBC05',
                    'Negative': '#EA4335'
                },
                template="plotly_white",
                range_x=[0, 100],
                labels={'Percentage': 'Percentage (%)'}
            )
            fig_sent.update_layout(showlegend=False, yaxis={'categoryorder':'trace'})
            st.plotly_chart(fig_sent, width="stretch")
            
        st.subheader("📋 Interaction Logs")
        st.dataframe(df[['timestamp', 'user', 'mode', 'student_message', 'bot_response', 'sentiment']], width="stretch")
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
