
import pytest
import hashlib
from database import (
    set_db_path, init_db, add_user, authenticate_user, 
    log_interaction_db, get_user_history, get_all_logs,
    get_courses_db, get_policies_db, add_appointment_db, get_appointments_db
)

@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test.db"
    set_db_path(db_file)
    init_db()
    return db_file

def test_user_operations(test_db):
    # Registration
    pw_hash = hashlib.sha256("pass123".encode()).hexdigest()
    success, msg = add_user("testuser", pw_hash, "student")
    assert success is True
    
    # Duplicate registration
    success, msg = add_user("testuser", pw_hash, "student")
    assert success is False
    
    # Authentication
    role = authenticate_user("testuser", pw_hash)
    assert role == "student"
    
    # Failed Auth
    assert authenticate_user("testuser", "wronghash") is None

def test_interaction_logs(test_db):
    log_interaction_db("user1", "AI", "Q1", "R1", 0.5)
    log_interaction_db("user1", "Local", "Q2", "R2", -0.2)
    
    history = get_user_history("user1", limit=10)
    assert len(history) == 4
    assert history[0]['content'] == "Q1"
    
    all_logs = get_all_logs()
    assert len(all_logs) == 2
    assert all_logs[0]['student_message'] == "Q2" # Ordered by timestamp DESC

def test_course_and_policies(test_db):
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO courses (id, name, department, description, interests, duration) VALUES (?,?,?,?,?,?)",
                   ("C1", "Test Course", "Dept", "Desc", "i1,i2", "1 year"))
    cursor.execute("INSERT INTO policies (topic, description) VALUES (?,?)",
                   ("Attendance", "75% required"))
    conn.commit()
    conn.close()
    
    courses = get_courses_db()
    assert len(courses) == 1
    assert courses[0]['name'] == "Test Course"
    
    policies = get_policies_db()
    assert len(policies) == 1
    assert policies[0]['topic'] == "Attendance"

def test_appointments(test_db):
    add_appointment_db("Manik", "MCA", "2026-06-10", "10:00")
    appts = get_appointments_db()
    assert len(appts) == 1
    assert appts[0]['student_name'] == "Manik"
    assert appts[0]['date'] == "2026-06-10"
