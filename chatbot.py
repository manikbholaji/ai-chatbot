import json
from pathlib import Path
from datetime import datetime
# Load Knowledge Base
BASE_DIR = Path(__file__).resolve().parent

def project_path(*parts):
    return BASE_DIR.joinpath(*parts)

def load_data():
    courses_path = project_path("data", "courses.json")
    policies_path = project_path("data", "policies.json")
    
    courses = []
    policies = []
    
    if courses_path.exists():
        with open(courses_path, "r") as f:
            courses = json.load(f).get("courses", [])
    if policies_path.exists():
        with open(policies_path, "r") as f:
            policies = json.load(f).get("policies", [])
    return courses, policies

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
        
        appointment = {
            "student_name": student_name,
            "course_name": course_name,
            "date": date,
            "time": time,
            "timestamp": datetime.now().isoformat()
        }
        
        appointments_file = project_path("data", "appointments.json")
        appointments = []
        if appointments_file.exists():
            with open(appointments_file, "r") as f:
                appointments = json.load(f)
            
        appointments.append(appointment)
        with open(appointments_file, "w") as f:
            json.dump(appointments, f, indent=2)
            
        return f"Success: Appointment booked for {student_name} on {date} at {time} for {course_name}."
    except Exception as e:
        return f"Error: {str(e)}"

def get_local_response(query):
    """
    Fast local lookup for common questions with refined matching.
    """
    query_clean = query.lower().strip()
    
    # 1. Search for courses (Improved matching)
    course_keywords = ["course", "degree", "study", "program", "admission", "department"]
    if any(k in query_clean for k in course_keywords) or any(c["name"].lower() in query_clean for c in COURSES):
        matched_courses = []
        for course in COURSES:
            course_name = course["name"].lower()
            course_interests = [i.lower() for i in course.get("interests", [])]
            
            # Match by name, interest, or specific keywords in query
            if course_name in query_clean or any(interest in query_clean for interest in course_interests):
                matched_courses.append(course)
        
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
        if topic in query_clean or (any(k in query_clean for k in policy_keywords) and topic.split()[0] in query_clean):
            return f"According to CU Policy on {policy['topic']}: {policy['description']}"

    # 3. Direct Greeting/Identity
    greetings = ["hi", "hello", "hey", "who are you", "what can you do"]
    if any(query_clean == g for g in greetings) or "help" in query_clean and len(query_clean) < 10:
        return "Hello! I am your CU Academic Advisor. I can help you with course information, university policies, and booking appointments. How can I assist you today?"

    return None

SYSTEM_PROMPT = f"""
You are the Chandigarh University (CU) Student Academic Advisor. Your goal is to help students find the right course and book appointments.

KNOWLEDGE BASE:
Courses: {json.dumps(COURSES)}
Policies: {json.dumps(POLICIES)}

GUIDELINES:
1. Be polite and professional.
2. Suggest courses from the KNOWLEDGE BASE based on interests.
3. Offer to book an appointment (9 AM - 5 PM, Mon-Fri) if they confirm interest.
"""

