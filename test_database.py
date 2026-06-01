import pytest
import hashlib
from sqlalchemy import create_engine
from database import (
    set_test_engine, init_db, add_user, authenticate_user, 
    log_interaction_db, get_user_history, get_all_logs,
    get_courses_db, get_policies_db, add_appointment_db, get_appointments_db,
    Course, Policy
)

@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}")
    set_test_engine(engine)
    init_db()
    return engine

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
    from database import get_session
    db = get_session()
    db.add(Course(id="C1", name="Test Course", department="Dept", description="Desc", interests="i1,i2", duration="1 year"))
    db.add(Policy(topic="Attendance", description="75% required"))
    db.commit()
    db.close()
    
    courses = get_courses_db()
    assert len(courses) >= 1 # Might have default data too
    assert any(c['name'] == "Test Course" for c in courses)
    
    policies = get_policies_db()
    assert len(policies) >= 1
    assert any(p['topic'] == "Attendance" for p in policies)

def test_appointments(test_db):
    add_appointment_db("Manik", "MCA", "2026-06-10", "10:00")
    appts = get_appointments_db()
    assert len(appts) == 1
    assert appts[0]['student_name'] == "Manik"
    assert appts[0]['date'] == "2026-06-10"
