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
    Fast local lookup for common questions with strict intent matching.
    """
    query_clean = query.lower().strip()
    
    # 1. Search for courses (Broad Keyword Match)
    academic_keywords = ["course", "degree", "engineering", "coding", "software", "study", "bachelor", "master", "mca", "mba"]
    if any(keyword in query_clean for keyword in academic_keywords):
        matched_courses = []
        for course in COURSES:
            # Check for name match or interest match
            course_name = course["name"].lower()
            course_interests = [i.lower() for i in course.get("interests", [])]
            
            if any(word in query_clean for word in course_name.split()) or \
               any(interest in query_clean for interest in course_interests):
                matched_courses.append(course)
        
        if matched_courses:
            response = "Based on your interests, I recommend the following courses at Chandigarh University:\n\n"
            for c in matched_courses:
                response += f"- **{c['name']}**: {c['description']} (Duration: {c['duration']})\n"
            response += "\nWould you like me to book an academic advising appointment for any of these?"
            return response

    # 2. Search for policies (Strict Intent)
    policy_keywords = ["policy", "attendance", "admission", "appointment", "rule"]
    if any(keyword in query_clean for keyword in policy_keywords):
        for policy in POLICIES:
            if policy["topic"].lower() in query_clean:
                return f"According to CU Policy on {policy['topic']}: {policy['description']}"

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

