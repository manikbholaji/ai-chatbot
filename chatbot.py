import os
import requests
from datetime import datetime
import json
import re
import streamlit as st
from database import get_courses_db, get_policies_db, add_appointment_db

# Enhanced Course List for MCA Project Perfection
EXTRA_COURSES = [
    {"id": "msc_ds", "name": "MSc Data Science", "description": "Advanced analytics and machine learning program.", "interests": ["data", "ai", "math", "statistics"], "duration": "2 Years"},
    {"id": "be_me", "name": "BE Mechanical Engineering", "description": "Study of machines, design, and manufacturing.", "interests": ["physics", "machines", "design"], "duration": "4 Years"},
    {"id": "b_arch", "name": "Bachelor of Architecture", "description": "Design and construction of buildings.", "interests": ["design", "art", "drawing", "construction"], "duration": "5 Years"},
    {"id": "llb", "name": "Bachelor of Laws (LLB)", "description": "Professional degree in law and legal studies.", "interests": ["law", "politics", "debate"], "duration": "3 Years"},
    {"id": "b_des_fashion", "name": "Bachelor of Design (B.Des) - Fashion Design", "description": "A creative program covering fashion illustration, apparel design, styling, and garment construction.", "interests": ["fashion", "designing", "style", "clothing", "apparel", "art"], "duration": "4 Years"},
    {"id": "bsc_animation", "name": "B.Sc in Animation, VFX and Gaming", "description": "A professional program in 3D modeling, animation, visual effects, and game development.", "interests": ["animation", "vfx", "gaming", "art", "design"], "duration": "3 Years"},
    {"id": "bsc_biotech", "name": "B.Sc (Hons) in Biotechnology", "description": "An interdisciplinary program exploring genetics, biochemistry, and molecular biology.", "interests": ["biology", "biotech", "science", "research", "medical"], "duration": "3 Years"},
    {"id": "ba_journalism", "name": "B.A. in Journalism and Mass Communication", "description": "Professional training in media reporting, news writing, TV production, and digital journalism.", "interests": ["journalism", "media", "writing", "news", "reporting", "tv"], "duration": "3 Years"}
]

# Load Knowledge Base from RDBMS
@st.cache_data
def load_data():
    try:
        courses = get_courses_db()
        policies = get_policies_db()
        
        # Fallback to static data if DB is empty but accessible
        if not courses:
            courses = [
                {"id": "mca", "name": "Master of Computer Applications", "description": "Professional Master's", "interests": "coding,software", "duration": "2 Years"},
                {"id": "be_cse", "name": "BE Computer Science", "description": "Engineering Degree", "interests": "logic,programming", "duration": "4 Years"}
            ]
        if not policies:
            policies = [{"topic": "Attendance", "description": "75% required."}]

        # Create a new list to avoid mutating any internal ORM results or causing cache issues
        merged_courses = []
        for c in courses:
            c_copy = dict(c)
            if isinstance(c_copy.get('interests'), str):
                c_copy['interests'] = [i.strip().lower() for i in c_copy['interests'].split(",")] if c_copy['interests'] else []
            merged_courses.append(c_copy)

        # Merge with EXTRA_COURSES if not already present
        for ec in EXTRA_COURSES:
            if not any(c['id'] == ec['id'] for c in merged_courses):
                merged_courses.append(ec)
                
        return merged_courses, policies
    except Exception as e:
        # Emergency static fallback for deployment stability
        print(f"Database loading failed: {str(e)}. Using static fallback.")
        fallback_courses = [
            {"id": "mca", "name": "Master of Computer Applications", "description": "Professional Master's", "interests": ["coding", "software"], "duration": "2 Years"}
        ]
        for ec in EXTRA_COURSES:
            if not any(c['id'] == ec['id'] for c in fallback_courses):
                fallback_courses.append(ec)
        return fallback_courses, [{"topic": "Attendance", "description": "75% required."}]

COURSES, POLICIES = load_data()

def book_appointment(date, time, student_name, course_name):
    """
    Books an appointment for a student within standard working hours (9 AM - 5 PM, Mon-Fri).
    """
    try:
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        if dt.weekday() >= 5:
            return "Error: Appointments are only available Monday to Friday."
        if not (9 <= dt.hour < 17):
            return "Error: Appointments must be between 9:00 AM and 5:00 PM."
        
        add_appointment_db(student_name, course_name, date, time)
        return f"Success: Appointment booked for {student_name} on {date} at {time} for {course_name}."
    except Exception as e:
        return f"Error: {str(e)}"

def get_local_response(query):
    """
    Fast local lookup for common questions with refined matching.
    """
    query_clean = query.lower().strip()
    
    # 0. Logic/Meta Inquiry Handler
    logic_keywords = ["logic", "how do you", "why did you", "how it works", "recommending", "recommend"]
    if any(re.search(rf"\b{re.escape(k)}\b", query_clean) for k in logic_keywords):
        return ("My recommendation logic is based on matching your expressed interests (e.g., 'coding', 'business', 'science') "
                "directly with the core curriculum and career outcomes of Chandigarh University's programs. "
                "I look for specific keywords in your messages to suggest the most relevant academic paths.")

    # 1. Search for policies (Improved matching)
    policy_keywords = ["policy", "rule", "attendance", "appointment", "schedule", "timing", "admission", "criteria"]
    for policy in POLICIES:
        topic = policy["topic"].lower()
        
        # Safe singularization (avoid stripping 'ss' like 'class' -> 'cla')
        def get_singular(w):
            if w.endswith('ss'):
                return w
            if w.endswith('s') and len(w) > 1:
                return w[:-1]
            return w

        topic_singular = get_singular(topic)
        topic_pattern = rf"\b{re.escape(topic_singular)}s?\b"
        
        has_topic_match = re.search(topic_pattern, query_clean) is not None
        
        has_keyword_match = False
        if any(re.search(rf"\b{re.escape(k)}\b", query_clean) for k in policy_keywords):
            topic_words = [get_singular(w) for w in topic.split()]
            if any(re.search(rf"\b{re.escape(word)}s?\b", query_clean) for word in topic_words):
                has_keyword_match = True

        if has_topic_match or has_keyword_match:
            return f"According to CU Policy on **{policy['topic']}**:\n\n{policy['description']}"

    # 2. Search for courses (with strict intent checking)
    academic_intents = [
        "course", "program", "degree", "study", "major", "recommend", "learn", "career", "class", 
        "admission", "department", "offer", "btech", "mca", "bca", "mba", "bsc", "llb", "b.des", 
        "b.sc", "b.a", "master", "bachelor", "interest", "interested", "looking for", "want to", "suggest"
    ]
    
    has_academic_intent = any(re.search(rf"\b{re.escape(intent)}\b", query_clean) for intent in academic_intents)
    
    # Check if a course name is mentioned directly
    has_direct_course_name = False
    for course in COURSES:
        if re.search(rf"\b{re.escape(course['name'].lower())}\b", query_clean):
            has_direct_course_name = True
            break
            
    if not (has_academic_intent or has_direct_course_name):
        return None

    matched_courses = []
    for course in COURSES:
        course_name = course["name"].lower()
        interests_raw = course.get("interests", [])
        if isinstance(interests_raw, str):
            course_interests = [i.strip().lower() for i in interests_raw.split(",")]
        else:
            course_interests = [i.lower() for i in interests_raw]
        
        name_match = re.search(rf"\b{re.escape(course_name)}\b", query_clean)
        interest_match = any(re.search(rf"\b{re.escape(interest)}\b", query_clean) for interest in course_interests)
        
        if name_match or interest_match:
            matched_courses.append(course)
    
    if matched_courses:
        response = "Based on your interests, I recommend the following courses at Chandigarh University:\n\n"
        for c in matched_courses[:5]: # Limit to top 5 for better UI
            response += f"- **{c['name']}**: {c['description']} (Duration: {c['duration']})\n"
        response += "\nWould you like me to book an academic advising appointment to discuss these further?"
        return response

    return None

SYSTEM_PROMPT = f"""
You are the Chandigarh University (CU) Student Academic Advisor. Your goal is to help students find the right course and book appointments.

KNOWLEDGE BASE:
Courses: {json.dumps(COURSES)}
Policies: {json.dumps(POLICIES)}

GUIDELINES:
1. Be polite and professional. Always prioritize answering the user's specific inquiry directly before providing general recommendations.
2. If the user asks about your logic, identity, or how you operate, explain that you are an AI advisor designed to match student interests with CU's academic offerings.
3. Suggest courses from the KNOWLEDGE BASE only when they align with the student's expressed interests or when the user asks for options.
4. Offer to book an academic advising appointment (9 AM - 5 PM, Mon-Fri) if the student shows interest in specific programs or needs professional guidance.
"""

def get_ai_response(messages):
    """
    Calls the Puter AI API (OpenAI compatible) using the token from Streamlit secrets.
    """
    token = None
    try:
        token = st.secrets.get("PUTER_TOKEN")
    except Exception:
        pass

    if not token:
        # Fallback for testing/local development
        if os.getenv("TESTING") == "true":
            last_user_msg = ""
            for m in reversed(messages):
                if m["role"] == "user":
                    last_user_msg = m["content"].lower()
                    break
            if "france" in last_user_msg:
                return {"status": "success", "content": "The capital of France is Paris."}
            return {"status": "success", "content": "This is a mock AI response for testing."}
        return {"status": "error", "message": "API token missing."}

    url = "https://api.puter.com/puterai/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}
