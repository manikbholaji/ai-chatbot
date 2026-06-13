
import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from chatbot import get_local_response, SYSTEM_PROMPT, book_appointment, get_ai_response
from database import (
    authenticate_user, add_user, log_interaction_db, 
    get_user_history, get_all_logs, get_appointments_db,
    is_production_db, get_db_error, delete_appointment_db
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
    db_status = "Production (Aiven)" if is_production_db() else "Offline / Connection Failed"
    db_icon = "🟢" if is_production_db() else "🔴"
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
    from datetime import datetime
    st.title("📅 Book Academic Advising Appointment")
    st.write("Schedule a session with an academic advisor to discuss your course options.")
    
    # 1. Advisor Profiles Section (Directory Grid)
    st.write("### 👥 Choose an Academic Advisor")
    st.caption("Review advisor specialties and availability. Click 'Select Advisor' to prefill the booking form below.")
    
    advisors_list = [
        {
            "name": "General Academic Advisor",
            "role": "General Advising",
            "desc": "Assists with general academic policies, registration, and general queries.",
            "color": "#4285F4",
            "initials": "GA",
            "hours": "Mon-Fri, 9:00 AM - 5:00 PM"
        },
        {
            "name": "Dr. Satish Kumar (Computer Science & IT)",
            "role": "Computer Science & IT",
            "desc": "Expert guidance on BCA, MCA, and BE-CSE courses and careers.",
            "color": "#34A853",
            "initials": "SK",
            "hours": "Mon-Fri, 10:00 AM - 4:00 PM"
        },
        {
            "name": "Dr. Neha Sharma (Biotechnology & Science)",
            "role": "Biotechnology & Science",
            "desc": "Academic pathways for BSc Biotechnology and science departments.",
            "color": "#FBBC05",
            "initials": "NS",
            "hours": "Mon-Fri, 11:00 AM - 3:00 PM"
        },
        {
            "name": "Prof. Amit Verma (Management & Commerce)",
            "role": "Management & Commerce",
            "desc": "Strategic advising for MBA and other business management programs.",
            "color": "#EA4335",
            "initials": "AV",
            "hours": "Mon-Fri, 9:00 AM - 2:00 PM"
        },
        {
            "name": "Dr. Priya Sen (Design & Fashion Arts)",
            "role": "Design & Fashion Arts",
            "desc": "Advises on B.Des Fashion Design, Animation, VFX, and Creative Arts.",
            "color": "#9C27B0",
            "initials": "PS",
            "hours": "Mon-Fri, 1:00 PM - 5:00 PM"
        }
    ]
    
    # Render advisor directory in columns
    adv_cols = st.columns(3)
    for index, adv in enumerate(advisors_list):
        col = adv_cols[index % 3]
        with col:
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; min-height: 250px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 15px; border-top: 4px solid {adv['color']};">
                <div>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background-color: {adv['color']}20; color: {adv['color']}; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1rem;">
                            {adv['initials']}
                        </div>
                        <div>
                            <h4 style="margin: 0; color: #1e1e1e; font-size: 1.05rem;">{adv['name'].split(" (")[0]}</h4>
                            <span style="font-size: 0.8rem; color: {adv['color']}; font-weight: 600; text-transform: uppercase;">{adv['role']}</span>
                        </div>
                    </div>
                    <p style="font-size: 0.85rem; color: #5f6368; line-height: 1.4; margin-bottom: 8px;">{adv['desc']}</p>
                </div>
                <div style="font-size: 0.8rem; color: #3c4043; border-top: 1px solid #eee; padding-top: 8px; margin-top: 8px;">
                    📅 <b>Hours:</b> {adv['hours']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Select advisor button
            if st.button(f"👉 Select {adv['name'].split()[0]}", key=f"select_adv_{index}", use_container_width=True):
                st.session_state.selected_advisor = adv['name']
                st.toast(f"Selected {adv['name']}!")
                st.rerun()

    st.write("---")
    
    # 2. The Booking Form Section
    st.write("### 📝 Enter Appointment Details")
    
    # Pre-select advisor if clicked above
    advisor_names_form = [a["name"] for a in advisors_list]
    default_idx = 0
    if "selected_advisor" in st.session_state and st.session_state.selected_advisor in advisor_names_form:
        default_idx = advisor_names_form.index(st.session_state.selected_advisor)
        
    with st.form("book_appt_form"):
        advisor_name = st.selectbox("Select Academic Advisor", advisor_names_form, index=default_idx)
        
        col_d, col_t = st.columns(2)
        with col_d:
            appt_date = st.date_input("Select Date")
        with col_t:
            appt_time_slot = st.selectbox("Select Time Slot (Mon-Fri, 9 AM - 5 PM)", [
                "09:00 - 10:00 AM",
                "10:00 - 11:00 AM",
                "11:00 - 12:00 PM",
                "01:00 - 02:00 PM",
                "02:00 - 03:00 PM",
                "03:00 - 04:00 PM",
                "04:00 - 05:00 PM"
            ])
            
        course_topic = st.text_input("Topic/Course of Interest", placeholder="e.g. Master of Computer Applications")
        
        submit_booking = st.form_submit_button("Book Appointment", use_container_width=True)
        
        if submit_booking:
            if not is_production_db():
                st.error("⚠️ Appointment booking is disabled because the database is offline.")
            elif not course_topic:
                st.error("Please enter a topic or course of interest.")
            elif appt_date.weekday() >= 5:
                st.error("Error: Advising is only available Monday to Friday.")
            else:
                date_str = appt_date.strftime("%Y-%m-%d")
                start_time = appt_time_slot.split(" - ")[0]
                time_part, ampm = start_time.split(" ")
                hr, mn = time_part.split(":")
                hr_num = int(hr)
                if ampm == "PM" and hr_num != 12:
                    hr_num += 12
                elif ampm == "AM" and hr_num == 12:
                    hr_num = 0
                time_str = f"{hr_num:02d}:{mn}"
                
                student_name = st.session_state.user['name']
                topic_str = f"{course_topic} (Advisor: {advisor_name})"
                
                result_msg = book_appointment(date_str, time_str, student_name, topic_str)
                if result_msg.startswith("Success"):
                    st.success(f"Success: Appointment booked with {advisor_name} on {date_str} at {time_part} {ampm} for {course_topic}.")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(result_msg)

    # 3. Student's Current Bookings Section
    st.write("---")
    st.write("### 📅 Your Scheduled Advising Sessions")
    
    student_appts = []
    try:
        all_appts = get_appointments_db()
        student_appts = [a for a in all_appts if a['student_name'] == st.session_state.user['name']]
    except Exception as exc:
        st.warning("⚠️ Could not load your schedules because the database is offline.")
        st.caption(f"Diagnostics: {str(exc)}")
        
    if student_appts:
        student_appts = sorted(student_appts, key=lambda x: f"{x['date']} {x['time']}")
        
        for idx, appt in enumerate(student_appts):
            advisor_part = "General Advisor"
            topic_part = appt['course_name']
            if "(Advisor:" in appt['course_name']:
                try:
                    parts = appt['course_name'].split(" (Advisor: ")
                    topic_part = parts[0]
                    advisor_part = parts[1].replace(")", "")
                except Exception:
                    pass
            
            appt_dt_str = f"{appt['date']} {appt['time']}"
            is_upcoming = datetime.strptime(appt_dt_str, "%Y-%m-%d %H:%M") >= datetime.now()
            status_text = "🟢 Upcoming" if is_upcoming else "🔵 Completed"
            status_color = "#34A853" if is_upcoming else "#4285F4"
            status_bg = "#e6f4ea" if is_upcoming else "#e8f0fe"
            
            card_col, cancel_col = st.columns([5, 1])
            with card_col:
                st.markdown(f"""
                <div style="background-color: white; padding: 16px; border-radius: 12px; border-left: 5px solid {status_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.01); border-top: 1px solid #f0f0f0; border-right: 1px solid #f0f0f0; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.1rem; font-weight: 700; color: #1e1e1e;">⏰ {appt['time']} | 📅 {appt['date']}</span><br/>
                        <span style="color: #3c4043; font-size: 0.9rem;"><b>Advisor:</b> {advisor_part}</span><br/>
                        <span style="color: #5f6368; font-size: 0.9rem;"><b>Advising Topic:</b> {topic_part}</span>
                    </div>
                    <div style="background-color: {status_bg}; color: {status_color}; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; text-align: center;">
                        {status_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with cancel_col:
                st.write("") 
                st.write("") 
                if st.button("❌ Cancel", key=f"cancel_std_appt_{idx}", use_container_width=True):
                    success = delete_appointment_db(appt['student_name'], appt['date'], appt['time'])
                    if success:
                        st.toast("Appointment cancelled!")
                        st.rerun()
                    else:
                        st.error("Failed to cancel.")
    else:
        st.info("You don't have any appointments booked yet. Use the form above to schedule your first session.")

# --- PAGE: CHAT HISTORY ---
elif st.session_state.page == "Chat History":
    from datetime import datetime
    st.title("📜 Conversation Logs")
    if not st.session_state.authenticated:
        st.warning("💡 Sign in via sidebar to access your persistent, professionally organized history.")
    else:
        u_name = st.session_state.user['name']
        history = None
        try:
            history = get_user_history(u_name, limit=100)
        except Exception as exc:
            st.warning("⚠️ Chat history is temporarily offline because the production database is unreachable.")
            st.caption(f"Diagnostics: {str(exc)}")
        
        if history:
            total_msgs = len(history)
            st.info(f"📊 **Session Analytics**: You have recorded **{total_msgs} messages** in your history context.")
            
            # Interactive Search and Advanced Filters
            st.write("### 🔍 Filter and Search Transcript")
            filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
            with filter_col1:
                search_query = st.text_input("Search keyword", placeholder="Type a keyword to filter history...", label_visibility="collapsed")
            with filter_col2:
                sort_order = st.selectbox("Sort by date", ["Newest First", "Oldest First"], label_visibility="collapsed")
            with filter_col3:
                sentiment_filter = st.selectbox("Filter by Sentiment", ["All Sentiments", "Positive 😊", "Neutral 😐", "Negative 😡"], label_visibility="collapsed")

            # Process turns
            turns = []
            import re
            for i in range(0, len(history), 2):
                if i+1 < len(history):
                    u_msg = history[i]
                    a_msg = history[i+1]
                    
                    blob = TextBlob(u_msg['content'])
                    pol = blob.sentiment.polarity
                    if pol > 0.1:
                        sent_label = "Positive 😊"
                        sent_color = "green"
                    elif pol < -0.1:
                        sent_label = "Negative 😡"
                        sent_color = "red"
                    else:
                        sent_label = "Neutral 😐"
                        sent_color = "orange"
                    
                    if sentiment_filter != "All Sentiments" and sentiment_filter != sent_label:
                        continue
                        
                    if search_query:
                        if (search_query.lower() not in u_msg['content'].lower() and 
                            search_query.lower() not in a_msg['content'].lower()):
                            continue
                            
                    turns.append({
                        "index": (i // 2) + 1,
                        "u_msg": u_msg,
                        "a_msg": a_msg,
                        "sentiment": pol,
                        "sentiment_label": sent_label,
                        "sentiment_color": sent_color
                    })
            
            if sort_order == "Newest First":
                turns = list(reversed(turns))
            
            # Mini Analytics Row for History
            st.write("### 📊 Personal Sentiment Insights")
            if turns:
                total_turns = len(turns)
                avg_sentiment = sum(t['sentiment'] for t in turns) / total_turns
                pos_count = sum(1 for t in turns if t['sentiment_label'] == "Positive 😊")
                neg_count = sum(1 for t in turns if t['sentiment_label'] == "Negative 😡")
                neu_count = sum(1 for t in turns if t['sentiment_label'] == "Neutral 😐")
                
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                with stats_col1:
                    st.metric("Total Turns", total_turns)
                with stats_col2:
                    st.metric("Avg Sentiment Score", f"{avg_sentiment:.2f}")
                with stats_col3:
                    st.metric("Sentiment Breakdown", f"🟢 {pos_count} | 🟡 {neu_count} | 🔴 {neg_count}")
                    
                # Mini Donut Chart
                fig_user_sent = px.pie(
                    names=["Positive 😊", "Neutral 😐", "Negative 😡"],
                    values=[pos_count, neu_count, neg_count],
                    color=["Positive 😊", "Neutral 😐", "Negative 😡"],
                    color_discrete_map={"Positive 😊": "#34A853", "Neutral 😐": "#FBBC05", "Negative 😡": "#EA4335"},
                    hole=0.4,
                    title="Your Query Mood Distribution",
                    template="plotly_white"
                )
                fig_user_sent.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_user_sent, use_container_width=True)
            
            # Download Transcript Button
            transcript_text = f"CU AI Advisor Transcript for {u_name}\n" + "="*40 + "\n"
            for msg in history:
                role_label = "Student" if msg['role'] == "user" else "Advisor"
                transcript_text += f"[{role_label}]: {msg['content']}\n\n"
                
            st.download_button(
                label="📥 Download Chat Transcript (.txt)",
                data=transcript_text,
                file_name=f"cu_advisor_transcript_{u_name}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.divider()
            
            st.write("### 📜 Chat Archive Timeline")
            if turns:
                for t in turns:
                    u_content = t['u_msg']['content']
                    a_content = t['a_msg']['content']
                    
                    if search_query:
                        pattern = re.compile(rf"({re.escape(search_query)})", re.IGNORECASE)
                        u_content = pattern.sub(r"<mark style='background-color: #ffe0b2; border-radius: 4px; padding: 2px 4px;'>\1</mark>", u_content)
                        a_content = pattern.sub(r"<mark style='background-color: #ffe0b2; border-radius: 4px; padding: 2px 4px;'>\1</mark>", a_content)
                    
                    exp_title = f"🗣️ Conversation Turn #{t['index']} | Query: \"{t['u_msg']['content'][:40]}...\" | {t['sentiment_label']}"
                    is_expanded = bool(search_query)
                    
                    with st.expander(exp_title, expanded=is_expanded):
                        st.markdown(f"**👤 Student:** {u_content}", unsafe_allow_html=True)
                        st.markdown(f"**🤖 Advisor:** {a_content}", unsafe_allow_html=True)
                        st.caption(f"Sentiment Polarity Score: {t['sentiment']:.2f}")
            else:
                st.caption("No matching messages found for your search filters.")
        elif history is not None:
            st.info("No recorded logs for this name.")

# --- PAGE: ADMIN DASHBOARD ---
elif st.session_state.page == "Admin Dashboard":
    st.title("📊 Advisor Analytics")
    logs = None
    try:
        logs = get_all_logs()
    except Exception as exc:
        st.warning("⚠️ Analytics dashboard is temporarily offline because the production database is unreachable.")
        st.caption(f"Diagnostics: {str(exc)}")
        
    if logs:
        df = pd.DataFrame(logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
        
        st.sidebar.markdown("### 🎛️ Analytics Filters")
        selected_user = st.sidebar.selectbox("Filter by Student", ["All"] + list(df['user'].unique()))
        selected_mode = st.sidebar.selectbox("Filter by Query Mode", ["All"] + list(df['mode'].unique()))
        
        df_filtered = df.copy()
        if selected_user != "All":
            df_filtered = df_filtered[df_filtered['user'] == selected_user]
        if selected_mode != "All":
            df_filtered = df_filtered[df_filtered['mode'] == selected_mode]
            
        # Top Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; align-items: center; gap: 15px;">
                <div style="width: 50px; height: 50px; border-radius: 10px; background-color: #4285F415; color: #4285F4; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">
                    💬
                </div>
                <div>
                    <span style="font-size: 0.85rem; color: #5f6368; font-weight: 600; text-transform: uppercase;">Total Queries</span>
                    <h2 style="margin: 0; color: #1e1e1e; font-size: 1.8rem; font-weight: 700;">{len(df_filtered)}</h2>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with m2:
            avg_sent = round(df_filtered['sentiment'].mean(), 2) if len(df_filtered) > 0 else 0.0
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; align-items: center; gap: 15px;">
                <div style="width: 50px; height: 50px; border-radius: 10px; background-color: #34A85315; color: #34A853; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">
                    😊
                </div>
                <div>
                    <span style="font-size: 0.85rem; color: #5f6368; font-weight: 600; text-transform: uppercase;">Avg Sentiment</span>
                    <h2 style="margin: 0; color: #1e1e1e; font-size: 1.8rem; font-weight: 700;">{avg_sent}</h2>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with m3:
            active_users = df_filtered['user'].nunique()
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; align-items: center; gap: 15px;">
                <div style="width: 50px; height: 50px; border-radius: 10px; background-color: #FBBC0515; color: #FBBC05; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">
                    👤
                </div>
                <div>
                    <span style="font-size: 0.85rem; color: #5f6368; font-weight: 600; text-transform: uppercase;">Active Students</span>
                    <h2 style="margin: 0; color: #1e1e1e; font-size: 1.8rem; font-weight: 700;">{active_users}</h2>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()
        
        tab_ov, tab_logs, tab_std = st.tabs(["📈 Dashboard Overview", "📋 Interaction Audit Logs", "👩‍🎓 Student Engagement"])
        
        with tab_ov:
            if not df_filtered.empty:
                c1, c2 = st.columns(2)
                
                with c1:
                    st.subheader("📈 Query Volume Over Time")
                    df_daily = df_filtered.set_index('timestamp').resample('D').count().reset_index()
                    fig_vol = px.line(df_daily, x='timestamp', y='student_message', labels={'student_message': 'Queries'},
                                      template="plotly_white", color_discrete_sequence=['#4285F4'], line_shape='spline')
                    fig_vol.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
                    st.plotly_chart(fig_vol, use_container_width=True)
                    
                with c2:
                    st.subheader("😊 Sentiment Distribution")
                    def classify_sentiment(score):
                        if score > 0.05:
                            return "Positive"
                        elif score < -0.05:
                            return "Negative"
                        else:
                            return "Neutral"
                    
                    df_filtered['sentiment_category'] = df_filtered['sentiment'].apply(classify_sentiment)
                    counts = df_filtered['sentiment_category'].value_counts()
                    total = len(df_filtered)
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
                    fig_sent.update_layout(showlegend=False, yaxis={'categoryorder':'trace'}, margin=dict(l=20, r=20, t=20, b=20), height=300)
                    st.plotly_chart(fig_sent, use_container_width=True)
                
                # Keyword Analytics Bar Chart
                st.subheader("🔑 Top Student Interest Keywords")
                all_interests = []
                for msg in df_filtered['student_message'].dropna():
                    words = [w.strip().lower() for w in msg.split() if len(w) > 3]
                    all_interests.extend(words)
                
                interest_counts = pd.Series(all_interests).value_counts().head(10).reset_index()
                interest_counts.columns = ['Keyword', 'Frequency']
                
                if not interest_counts.empty:
                    fig_keywords = px.bar(interest_counts, x='Keyword', y='Frequency', 
                                          color='Frequency', color_continuous_scale='Blues',
                                          template="plotly_white")
                    fig_keywords.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig_keywords, use_container_width=True)
            else:
                st.warning("No records match the selected filters.")
                
        with tab_logs:
            st.subheader("📋 Interaction Logs")
            search_table = st.text_input("🔍 Search interaction logs", placeholder="Type keywords to filter log rows...")
            
            df_table = df_filtered[['timestamp', 'user', 'mode', 'student_message', 'bot_response', 'sentiment']].copy()
            if search_table:
                df_table = df_table[
                    df_table['student_message'].str.contains(search_table, case=False, na=False) |
                    df_table['bot_response'].str.contains(search_table, case=False, na=False) |
                    df_table['user'].str.contains(search_table, case=False, na=False)
                ]
            
            def make_badge(s):
                if s > 0.1: return "🟢 Positive"
                elif s < -0.1: return "🔴 Negative"
                return "🟡 Neutral"
            df_table['Sentiment Badge'] = df_table['sentiment'].apply(make_badge)
            
            df_table_show = df_table[['timestamp', 'user', 'mode', 'student_message', 'bot_response', 'sentiment', 'Sentiment Badge']]
            st.dataframe(df_table_show, use_container_width=True)
            
            st.download_button(
                label="📥 Export Logs to CSV",
                data=df_table.to_csv(index=False),
                file_name="cu_advisor_logs.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with tab_std:
            st.subheader("👩‍🎓 Student Engagement Summary")
            if not df_filtered.empty:
                student_stats = df_filtered.groupby('user').agg(
                    Total_Queries=('student_message', 'count'),
                    Avg_Sentiment=('sentiment', 'mean')
                ).reset_index().sort_values('Total_Queries', ascending=False)
                
                fig_std = px.bar(
                    student_stats, x='user', y='Total_Queries', color='Avg_Sentiment',
                    color_continuous_scale='RdYlGn', labels={'user': 'Student Username', 'Total_Queries': 'Queries Count'},
                    title="Queries Count and Avg Sentiment by Student", template="plotly_white"
                )
                st.plotly_chart(fig_std, use_container_width=True)
                
                st.dataframe(student_stats, use_container_width=True)
            else:
                st.info("No query logs available for student engagement analysis.")
                
    elif logs is not None:
        st.info("No logs collected yet.")

# --- PAGE: APPOINTMENT MANAGEMENT ---
elif st.session_state.page == "Appointment Management":
    st.title("📅 Appointment Management Dashboard")
    appts = None
    try:
        appts = get_appointments_db()
    except Exception as exc:
        st.warning("⚠️ Appointment list is temporarily offline because the production database is unreachable.")
        st.caption(f"Diagnostics: {str(exc)}")
        
    if appts:
        df = pd.DataFrame(appts)
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df = df.sort_values('datetime', ascending=True)
        
        # Summary KPI cards
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; align-items: center; gap: 15px;">
                <div style="width: 50px; height: 50px; border-radius: 10px; background-color: #4285F415; color: #4285F4; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">
                    📅
                </div>
                <div>
                    <span style="font-size: 0.85rem; color: #5f6368; font-weight: 600; text-transform: uppercase;">Total Bookings</span>
                    <h2 style="margin: 0; color: #1e1e1e; font-size: 1.8rem; font-weight: 700;">{len(df)}</h2>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col2:
            upcoming_count = len(df[df['datetime'] >= pd.Timestamp.now()])
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; align-items: center; gap: 15px;">
                <div style="width: 50px; height: 50px; border-radius: 10px; background-color: #34A85315; color: #34A853; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">
                    ⏰
                </div>
                <div>
                    <span style="font-size: 0.85rem; color: #5f6368; font-weight: 600; text-transform: uppercase;">Upcoming Sessions</span>
                    <h2 style="margin: 0; color: #1e1e1e; font-size: 1.8rem; font-weight: 700;">{upcoming_count}</h2>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col3:
            unique_students = df['student_name'].nunique()
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; align-items: center; gap: 15px;">
                <div style="width: 50px; height: 50px; border-radius: 10px; background-color: #FBBC0515; color: #FBBC05; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">
                    👩‍🎓
                </div>
                <div>
                    <span style="font-size: 0.85rem; color: #5f6368; font-weight: 600; text-transform: uppercase;">Unique Students</span>
                    <h2 style="margin: 0; color: #1e1e1e; font-size: 1.8rem; font-weight: 700;">{unique_students}</h2>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()

        # Split into tabs: Sched & Load
        tab_sched, tab_load = st.tabs(["🗓️ Active Schedule", "📊 Advisor Load Analytics"])
        
        with tab_load:
            st.subheader("📊 Advisor Appointment Distribution")
            def get_advisor_name(c):
                if "(Advisor:" in c:
                    try:
                        return c.split(" (Advisor: ")[1].replace(")", "")
                    except Exception:
                        return "General Advisor"
                return "General Advisor"
            
            df['Advisor'] = df['course_name'].apply(get_advisor_name)
            advisor_workload = df['Advisor'].value_counts().reset_index()
            advisor_workload.columns = ['Advisor', 'Bookings']
            
            fig_load = px.bar(
                advisor_workload, y='Advisor', x='Bookings', orientation='h',
                color='Bookings', color_continuous_scale='Purples',
                title="Total Bookings by Advisor", template="plotly_white"
            )
            fig_load.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_load, use_container_width=True)

        with tab_sched:
            st.write("### 🎛️ Schedule Filters")
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                search_student = st.text_input("Search Student Name", placeholder="Type student name...")
            with f_col2:
                filter_advisor_name = st.selectbox("Filter by Advisor", ["All Advisors"] + list(df['course_name'].apply(get_advisor_name).unique()))
            with f_col3:
                filter_status = st.selectbox("Filter by Status", ["All Sessions", "🟢 Upcoming Only", "🔵 Completed Only"])
            
            # Apply filters
            df_filtered_appts = df.copy()
            if search_student:
                df_filtered_appts = df_filtered_appts[df_filtered_appts['student_name'].str.contains(search_student, case=False, na=False)]
            
            if filter_advisor_name != "All Advisors":
                df_filtered_appts = df_filtered_appts[df_filtered_appts['course_name'].apply(get_advisor_name) == filter_advisor_name]
                
            if filter_status == "🟢 Upcoming Only":
                df_filtered_appts = df_filtered_appts[df_filtered_appts['datetime'] >= pd.Timestamp.now()]
            elif filter_status == "🔵 Completed Only":
                df_filtered_appts = df_filtered_appts[df_filtered_appts['datetime'] < pd.Timestamp.now()]
                
            # Export Schedule to CSV
            st.download_button(
                label="📥 Export Schedule to CSV",
                data=df_filtered_appts[['date', 'time', 'student_name', 'course_name', 'timestamp']].to_csv(index=False),
                file_name="cu_advising_schedule.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.subheader("📅 Scheduled Sessions Timeline")
            
            if not df_filtered_appts.empty:
                for date, group in df_filtered_appts.groupby('date'):
                    st.markdown(f"#### 📅 {pd.to_datetime(date).strftime('%A, %d %B %Y')}")
                    
                    for idx, row in group.iterrows():
                        is_upcoming = pd.to_datetime(row['date'] + ' ' + row['time']) >= pd.Timestamp.now()
                        status_badge = "🟢 Upcoming" if is_upcoming else "🔵 Completed"
                        
                        adv_name_parsed = get_advisor_name(row['course_name'])
                        topic_cleaned = row['course_name'].split(" (Advisor: ")[0] if "(Advisor: " in row['course_name'] else row['course_name']
                        
                        card_col, action_col = st.columns([5, 1.2])
                        with card_col:
                            st.markdown(f"""
                            <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid {'#34A853' if is_upcoming else '#4285F4'}; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.01); border-top: 1px solid #f0f0f0; border-right: 1px solid #f0f0f0; border-bottom: 1px solid #f0f0f0;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 1.15rem; font-weight: 700; color: #1e1e1e;">⏰ {row['time']}</span>
                                    <span style="background-color: {'#e6f4ea' if is_upcoming else '#e8f0fe'}; color: {'#137333' if is_upcoming else '#1a73e8'}; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">{status_badge}</span>
                                </div>
                                <p style="margin: 8px 0 0 0; color: #3c4043; font-size: 0.95rem;"><b>Student:</b> {row['student_name']}</p>
                                <p style="margin: 4px 0 0 0; color: #3c4043; font-size: 0.95rem;"><b>Advisor:</b> {adv_name_parsed}</p>
                                <p style="margin: 4px 0 0 0; color: #5f6368; font-size: 0.95rem;"><b>Advising Topic:</b> {topic_cleaned}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with action_col:
                            st.write("") 
                            st.write("")
                            if st.button("❌ Cancel", key=f"cancel_admin_appt_{row['student_name']}_{row['date']}_{row['time']}", use_container_width=True):
                                success = delete_appointment_db(row['student_name'], row['date'], row['time'])
                                if success:
                                    st.success(f"Cancelled session!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete.")
                    st.divider()
            else:
                st.caption("No appointments found matching your filters.")
    elif appts is not None:
        st.info("No appointments found.")

st.sidebar.markdown("---")
st.sidebar.caption("MCA Final Project | Serverless AI Architecture")
