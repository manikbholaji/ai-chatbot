
import sqlite3
from pathlib import Path
from datetime import datetime
import json
import re
from database import get_courses_db, get_policies_db, add_appointment_db

# Load Knowledge Base from RDBMS
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

        # Format courses to include list of interests
        for c in courses:
            if isinstance(c.get('interests'), str):
                c['interests'] = c['interests'].split(",") if c['interests'] else []
                
        return courses, policies
    except Exception as e:
        # Emergency static fallback for deployment stability
        print(f"Database loading failed: {str(e)}. Using static fallback.")
        return [
            {"id": "mca", "name": "Master of Computer Applications", "description": "Professional Master's", "interests": ["coding", "software"], "duration": "2 Years"}
        ], [{"topic": "Attendance", "description": "75% required."}]

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

    # 1. Search for courses (Improved matching with word boundaries)
    course_keywords = ["course", "degree", "study", "program", "admission", "department"]
    has_course_context = any(re.search(rf"\b{re.escape(k)}s?\b", query_clean) for k in course_keywords)
    
    if has_course_context or any(re.search(rf"\b{re.escape(c['name'].lower())}\b", query_clean) for c in COURSES):
        matched_courses = []
        for course in COURSES:
            course_name = course["name"].lower()
            course_interests = [i.lower() for i in course.get("interests", [])]
            
            name_match = re.search(rf"\b{re.escape(course_name)}\b", query_clean)
            interest_match = any(re.search(rf"\b{re.escape(interest)}\b", query_clean) for interest in course_interests)
            
            if name_match or interest_match:
                matched_courses.append(course)
        
        if not matched_courses and has_course_context:
            matched_courses = COURSES
            
        if matched_courses:
            response = "Based on your interests, I recommend the following courses at Chandigarh University:\n\n"
            for c in matched_courses:
                response += f"- **{c['name']}**: {c['description']} (Duration: {c['duration']})\n"
            response += "\nWould you like me to book an academic advising appointment to discuss these further?"
            return response

    # 2. Search for policies (Improved matching)
    policy_keywords = ["policy", "rule", "attendance", "appointment", "schedule", "timing", "admission"]
    for policy in POLICIES:
        topic = policy["topic"].lower()
        topic_pattern = rf"\b{re.escape(topic.rstrip('s'))}s?\b"
        
        if re.search(topic_pattern, query_clean) or \
           (any(re.search(rf"\b{re.escape(k)}\b", query_clean) for k in policy_keywords) and \
            any(re.search(rf"\b{re.escape(word.rstrip('s'))}s?\b", query_clean) for word in topic.split())):
            return f"According to CU Policy on {policy['topic']}: {policy['description']}"

    # 3. Direct Greeting/Identity
    greetings = ["hi", "hello", "hey", "who are you", "what can you do"]
    if any(query_clean == g for g in greetings) or (re.search(rf"\bhelp\b", query_clean) and len(query_clean) < 10):
        return "Hello! I am your CU Academic Advisor. I can help you with course information, university policies, and booking appointments. How can I assist you today?"

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
