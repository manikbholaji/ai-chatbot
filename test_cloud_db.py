
import pytest
import hashlib
from database import (
    add_user, authenticate_user, log_interaction_db, get_user_history,
    add_appointment_db, get_appointments_db
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def db_session():
    # Use a fresh in-memory SQLite for testing to ensure no side effects
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    from database import Base
    Base.metadata.create_all(bind=engine)
    
    # Mock database.SessionLocal and Engine for the duration of the test
    import database
    original_session = database.SessionLocal
    database.SessionLocal = TestingSessionLocal
    
    yield TestingSessionLocal()
    
    # Cleanup
    database.SessionLocal = original_session

def test_cloud_ready_user_ops(db_session):
    # Register
    h = hashlib.sha256("cloud123".encode()).hexdigest()
    success, msg = add_user("cloud_user", h, "student")
    assert success is True
    
    # Authenticate
    role = authenticate_user("cloud_user", h)
    assert role == "student"

def test_cloud_ready_logs(db_session):
    log_interaction_db("cloud_user", "AI", "Hello Cloud", "Hello Manik", 0.9)
    history = get_user_history("cloud_user")
    assert len(history) == 2
    assert "Hello Cloud" in history[0]['content']

def test_cloud_ready_appointments(db_session):
    add_appointment_db("Manik", "Cloud Computing", "2026-07-01", "14:00")
    appts = get_appointments_db()
    assert len(appts) == 1
    assert appts[0]['course_name'] == "Cloud Computing"
