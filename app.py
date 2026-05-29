import streamlit as st
import json
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from chatbot import get_local_response, book_appointment, SYSTEM_PROMPT, get_advisor_response
from puter_bridge import puter_bridge
import uuid
import time
from dotenv import load_dotenv, set_key
import hashlib

load_dotenv(override=True)

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

# --- USER AUTHENTICATION SYSTEM ---
USERS_FILE = project_path("data", "users.json")

def init_db():
    os.makedirs(USERS_FILE.parent, exist_ok=True)
    if not USERS_FILE.exists():
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
        return False, "Username already exists."
    
    users[username] = {"password": hash_password(password)}
    save_users(users)
    return True, "Successfully registered! Please login."

def authenticate_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False

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

# --- SIGN OUT CALLBACK ---
def handle_sign_out():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.messages = []
    st.session_state.processing = False

# 1. Local Account System (Signup / Login)
with st.sidebar:
    st.markdown("### 🔐 User Account")
    
    if st.session_state.authenticated:
        st.success(f"Signed in as **{st.session_state.user['name']}**")
        
        # Display professional AI status consistent with anonymous mode
        if os.getenv("PUTER_AUTH_TOKEN"):
            st.info("✅ AI Mode: Enabled (Developer Powered)")
        else:
            st.success("✅ Client-Side AI: Enabled (Unlimited & Keyless)")
        
        st.button("Sign Out", on_click=handle_sign_out)
    else:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                st.markdown("**Login for persistent history**")
                login_user = st.text_input("Username")
                login_pass = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Login")
                if submit_login:
                    if authenticate_user(login_user, login_pass):
                        st.session_state.authenticated = True
                        st.session_state.user = {"name": login_user}
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                        
        with tab2:
            with st.form("signup_form"):
                st.markdown("**Create a new account**")
                reg_user = st.text_input("New Username")
                reg_pass = st.text_input("New Password", type="password")
                submit_reg = st.form_submit_button("Sign Up")
                if submit_reg:
                    if len(reg_user) < 3 or len(reg_pass) < 5:
                        st.error("Username must be >= 3 chars and password >= 5 chars.")
                    else:
                        success, msg = register_user(reg_user, reg_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
        
        st.success("✅ Client-Side AI: Enabled (Unlimited & Keyless)")

st.sidebar.markdown("---")
# Use session state to control the radio button
if "page" not in st.session_state:
    st.session_state.page = "Student Advisor"

# Dynamic Page List based on Role
pages = ["Student Advisor", "Chat History"]
if st.session_state.authenticated and st.session_state.user['name'] == "Manik":
    pages.append("Admin Dashboard")

# Ensure the current page is still in the allowed list (e.g. after logout)
if st.session_state.page not in pages:
    st.session_state.page = "Student Advisor"

page_index = pages.index(st.session_state.page) if st.session_state.page in pages else 0

page = st.sidebar.radio("Go to", pages, index=page_index, key="sidebar_nav")
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
            #### 🔒 Advanced Features
            **Login or Sign Up** in the sidebar to unlock **persistent chat history** and personalized advising.
        """)
        st.divider()

    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if isinstance(message["content"], dict) and message["content"].get("type") == "client_side_ai":
                prompt = message["content"].get("prompt")
                
                # PREPARE CONTEXT: Gather previous messages to personalize the response
                history_context = []
                # Include last 6 messages for context (3 exchanges)
                for m in st.session_state.messages[:i]:
                    if isinstance(m["content"], str):
                        history_context.append({"role": m["role"], "content": m["content"]})
                
                # Sanitize context for JS injection
                history_json = json.dumps(history_context).replace('"', '\\"').replace('\n', ' ')
                system_context = SYSTEM_PROMPT.replace('"', '\\"').replace('\n', ' ')
                
                # 100% Client-Side Puter AI Call (Bypasses Python Backend)
                puter_script = f"""
                <div id="puter-container" style="background-color: #f0f2f6; padding: 12px; border-radius: 12px; border-left: 5px solid #FF4B4B; min-height: 40px; margin-top: 5px;">
                    <div id="puter-output" style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #31333F; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; font-size: 15px;">
                        <div id="loader" style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 14px; height: 14px; border: 2px solid #FF4B4B; border-top: 2px solid transparent; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                            <i style="color: #666; font-size: 14px;">Personalizing advice...</i>
                        </div>
                    </div>
                </div>
                <style>
                    body {{ margin: 0; padding: 0; overflow: hidden; background: transparent; }}
                    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
                </style>
                <script src="https://js.puter.com/v2/"></script>
                <script>
                    const container = document.getElementById('puter-container');
                    const setHeight = () => {{
                        const height = document.body.scrollHeight || container.offsetHeight;
                        window.parent.postMessage({{
                            isStreamlitMessage: true,
                            type: "streamlit:setFrameHeight",
                            height: height + 10
                        }}, "*");
                    }};

                    const observer = new MutationObserver(setHeight);
                    observer.observe(container, {{ childList: true, subtree: true, characterData: true }});

                    const history = JSON.parse("{history_json}");
                    const messages = [
                        {{ role: "system", content: "{system_context}" }},
                        ...history,
                        {{ role: "user", content: "{prompt.replace('"', '\\"').replace('\n', ' ')}" }}
                    ];

                    puter.ai.chat(messages, {{ 
                        model: "openai/gpt-4o",
                        max_tokens: 1200 
                    }})
                        .then(response => {{
                            const output = document.getElementById('puter-output');
                            const content = typeof response === 'string' ? response : (response.message ? response.message.content : JSON.stringify(response));
                            output.innerText = content;
                            container.style.backgroundColor = "transparent";
                            container.style.padding = "0";
                            container.style.border = "none";
                            setHeight();
                        }})
                        .catch(err => {{
                            const output = document.getElementById('puter-output');
                            output.innerHTML = '<span style="color: #ff4b4b; font-weight: 500;">Connection Issue: Please check your internet.</span>';
                            setHeight();
                        }});
                </script>
                """
                st.components.v1.html(puter_script, height=400, scrolling=False)
            else:
                st.markdown(message["content"])

    # Processing indicator
    if st.session_state.processing:
        with st.chat_message("assistant"):
            st.write("Consulting AI Advisor for complex query... 🧠")

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
                # STEP 2: Logic didn't fit. Check if we should use Client-Side or Backend AI.
                if st.session_state.authenticated and os.getenv("PUTER_AUTH_TOKEN"):
                    st.session_state.processing = True
                    st.rerun()
                else:
                    # USE 100% CLIENT-SIDE AI (Anonymous / Keyless / Unlimited)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": {"type": "client_side_ai", "prompt": prompt}
                    })
                    log_interaction(prompt, "Triggered Client-Side Puter AI", 0, "Puter-Client")
                    st.rerun()

    # Handle Backend AI Processing (after rerun)
    if st.session_state.processing:
        ai_response = get_advisor_response(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        log_interaction(st.session_state.messages[-2]["content"], ai_response, 0, "AI-Backend")
        st.session_state.processing = False
        st.rerun()

elif page == "Chat History":
    st.title("📜 Your Chat History")
    
    if not st.session_state.authenticated:
        st.warning("💡 **Enter your name** in the sidebar to unlock your persistent, personalized chat history across sessions!")
        
        if st.session_state.messages:
            st.subheader("Current Session History")
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        else:
            st.info("No active conversation in this session.")
    else:
        current_user = st.session_state.user['name']
        log_file = "data/interaction_logs.jsonl"
        
        if os.path.exists(log_file):
            # Efficiently read and filter logs for current user
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
                
                # Sort by timestamp (newest first)
                df = df.sort_values('timestamp', ascending=False)
                
                dates = df['date'].unique()
                
                st.write(f"Showing chat history for **{current_user}**")
                
                for date in dates:
                    with st.expander(f"📅 {date.strftime('%B %d, %Y')}", expanded=(date == dates[0])):
                        day_logs = df[df['date'] == date].sort_values('timestamp', ascending=True)
                        for _, row in day_logs.iterrows():
                            # UI for each exchange
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
    
    # --- DEVELOPER SETUP SECTION ---
    with st.expander("🛠️ Developer Setup (Permanent AI Activation)", expanded=not os.getenv("PUTER_AUTH_TOKEN")):
        st.markdown("""
            **Instructions for the Maker:**
            To enable permanent AI mode for all users using your account:
            1. Click the **Google Sign In** button below.
            2. Once authenticated, the system will automatically capture your **Auth Token**.
            3. The token will be saved to your server's `.env` file, enabling AI mode permanently!
        """)
        
        # Hidden bridge for token capture
        setup_result = puter_bridge(command="get_token", key="maker_setup_bridge")
        
        if setup_result and setup_result.get('type') == 'maker_token':
            token = setup_result.get('token')
            maker_user = setup_result.get('user')
            
            # Save token to .env file
            env_path = project_path(".env")
            if not env_path.exists():
                with open(env_path, "w") as f:
                    f.write(f"PUTER_AUTH_TOKEN={token}\n")
            else:
                set_key(str(env_path), "PUTER_AUTH_TOKEN", token)
            
            st.success(f"✅ Successfully linked Maker Account: **{maker_user}**")
            st.info("Permanent AI mode is now active for all users! Please refresh the page.")
            if st.button("Refresh App Now"):
                st.rerun()

    # ... (Rest of analytics dashboard)
    log_file = "data/interaction_logs.jsonl"
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
