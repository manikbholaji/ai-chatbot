
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime
import os

BASE_DIR = Path(__file__).resolve().parent
Base = declarative_base()

# --- DATABASE MODELS ---

class User(Base):
    __tablename__ = 'users'
    username = Column(String(50), primary_key=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='student')

class Course(Base):
    __tablename__ = 'courses'
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    description = Column(Text)
    interests = Column(Text) # Comma-separated
    duration = Column(String(50))

class Policy(Base):
    __tablename__ = 'policies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

class InteractionLog(Base):
    __tablename__ = 'interaction_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now)
    user = Column(String(50))
    mode = Column(String(50))
    student_message = Column(Text)
    bot_response = Column(Text)
    sentiment = Column(Float)

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_name = Column(String(100))
    course_name = Column(String(100))
    date = Column(String(20))
    time = Column(String(20))
    timestamp = Column(DateTime, default=datetime.now)

# --- CONNECTION MANAGEMENT ---

@st.cache_resource
def get_engine():
    """
    Returns a SQLAlchemy engine. 
    Strictly uses Production PostgreSQL (via Streamlit Secrets).
    Falls back to SQLite ONLY during automated testing.
    """
    # 1. Check for Testing Environment (CI)
    if os.getenv("TESTING") == "true":
        return create_engine("sqlite:///:memory:")

    # 2. Production / Local development logic
    db_url = None
    try:
        if "DATABASE_URL" in st.secrets:
            db_url = st.secrets["DATABASE_URL"]
        else:
            db_config = st.secrets.get("database")
            if db_config:
                db_url = db_config.get("url")
    except Exception:
        pass

    if not db_url:
        local_db_path = BASE_DIR / "data" / "university.db"
        return create_engine(f"sqlite:///{local_db_path}", pool_pre_ping=True)
    
    db_url = db_url.strip()

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    try:
        # pool_pre_ping=True helps with dropped connections in cloud environments
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect():
            pass
        return engine
    except Exception as exc:
        raise ConnectionError(f"CRITICAL: Database connection failed: {exc}") from exc

def _read_secret_section(section_name):
    try:
        return st.secrets.get(section_name)
    except StreamlitSecretNotFoundError:
        return None

def _is_admin_bootstrap_enabled():
    env_value = os.getenv("ENABLE_ADMIN_BOOTSTRAP")
    if env_value is not None:
        return env_value.strip().lower() == "true"

    bootstrap_secrets = _read_secret_section("admin_bootstrap")
    if not bootstrap_secrets:
        return False

    enabled = bootstrap_secrets.get("enabled", False)
    if isinstance(enabled, bool):
        return enabled
    if isinstance(enabled, str):
        return enabled.strip().lower() == "true"
    return False

def _get_admin_bootstrap_credentials():
    username = os.getenv("ADMIN_BOOTSTRAP_USERNAME")
    password_hash = os.getenv("ADMIN_BOOTSTRAP_PASSWORD_HASH")

    if username and password_hash:
        return username, password_hash

    bootstrap_secrets = _read_secret_section("admin_bootstrap")
    if not bootstrap_secrets:
        return None, None

    return bootstrap_secrets.get("username"), bootstrap_secrets.get("password_hash")

# Initialize Global Engine
Engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

def set_test_engine(test_engine):
    """Overrides the global engine and session for testing."""
    global Engine, SessionLocal
    Engine = test_engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

def init_db():
    """
    Initializes the database schema and seeds default data.
    Safely handles connection errors during startup.
    """
    try:
        Base.metadata.create_all(bind=Engine)
        
        db = SessionLocal()
        
        # 1. Optional Admin Bootstrap
        if _is_admin_bootstrap_enabled():
            admin_username, admin_password_hash = _get_admin_bootstrap_credentials()
            if admin_username and admin_password_hash:
                existing_admin = db.query(User).filter(User.username == admin_username).first()
                if not existing_admin:
                    new_admin = User(username=admin_username, password_hash=admin_password_hash, role="admin")
                    db.add(new_admin)

        # 2. Default Courses
        if db.query(Course).count() == 0:
            default_courses = [
                Course(id="mca", name="Master of Computer Applications", department="Computer Applications", 
                       description="A professional master's degree in computer science.", 
                       interests="coding,software,apps,it", duration="2 Years"),
                Course(id="bca", name="Bachelor of Computer Applications", department="Computer Applications", 
                       description="Foundational undergraduate degree in computing.", 
                       interests="computers,programming,web", duration="3 Years"),
                Course(id="be_cse", name="BE Computer Science Engineering", department="Engineering", 
                       description="Premier engineering program for software development.", 
                       interests="engineering,logic,hardware,ai", duration="4 Years"),
                Course(id="mba", name="Master of Business Administration", department="Management", 
                       description="Advanced degree for leadership and business strategy.", 
                       interests="business,management,leadership", duration="2 Years")
            ]
            db.add_all(default_courses)
        
        if db.query(Policy).count() == 0:
            default_policies = [
                Policy(topic="Attendance", description="Students must maintain 75% attendance to be eligible for final examinations."),
                Policy(topic="Grading", description="Evaluation is based on a CGPA system with internal assessments and end-term exams."),
                Policy(topic="Admissions", description="Admissions are based on merit and CU-CET entrance examination results."),
                Policy(topic="Appointments", description="Academic advising is available Mon-Fri, 9 AM to 5 PM via the online portal.")
            ]
            db.add_all(default_policies)
        
        db.commit()
        db.close()
    except Exception as e:
        # Only print error during init, app.py will handle the UI error display
        print(f"Database Initialization Warning: {str(e)}")

# Auto-initialize database on import (Safe)
init_db()

# --- HELPER FUNCTIONS ---

def get_session():
    return SessionLocal()

def authenticate_user(username, password_hash):
    """
    Authenticates a user and returns their role strictly from the database.
    """
    db = get_session()
    user = db.query(User).filter(User.username == username, User.password_hash == password_hash).first()
    role = user.role if user else None
    db.close()
    return role

def add_user(username, password_hash, role='student'):
    db = get_session()
    try:
        new_user = User(username=username, password_hash=password_hash, role=role)
        db.add(new_user)
        db.commit()
        return True, "Account created!"
    except Exception:
        db.rollback()
        return False, "Username exists"
    finally:
        db.close()

def log_interaction_db(user, mode, message, response, sentiment):
    db = get_session()
    try:
        log = InteractionLog(user=user, mode=mode, student_message=message, bot_response=response, sentiment=sentiment)
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

def get_user_history(username, limit=10):
    db = get_session()
    logs = db.query(InteractionLog).filter(InteractionLog.user == username).order_by(InteractionLog.timestamp.desc()).limit(limit).all()
    db.close()
    
    history = []
    for log in reversed(logs):
        history.append({"role": "user", "content": log.student_message})
        history.append({"role": "assistant", "content": log.bot_response})
    return history

def get_all_logs():
    db = get_session()
    logs = db.query(InteractionLog).order_by(InteractionLog.timestamp.desc()).all()
    db.close()
    return [
        {
            "timestamp": entry.timestamp.isoformat(),
            "user": entry.user,
            "mode": entry.mode,
            "student_message": entry.student_message,
            "bot_response": entry.bot_response,
            "sentiment": entry.sentiment
        } for entry in logs
    ]

def get_courses_db():
    db = get_session()
    courses = db.query(Course).all()
    db.close()
    return [
        {
            "id": c.id,
            "name": c.name,
            "department": c.department,
            "description": c.description,
            "interests": c.interests,
            "duration": c.duration
        } for c in courses
    ]

def get_policies_db():
    db = get_session()
    policies = db.query(Policy).all()
    db.close()
    return [{"topic": p.topic, "description": p.description} for p in policies]

def add_appointment_db(student_name, course_name, date, time):
    db = get_session()
    try:
        appt = Appointment(student_name=student_name, course_name=course_name, date=date, time=time)
        db.add(appt)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_appointments_db():
    db = get_session()
    appts = db.query(Appointment).order_by(Appointment.date, Appointment.time).all()
    db.close()
    return [
        {
            "student_name": a.student_name,
            "course_name": a.course_name,
            "date": a.date,
            "time": a.time,
            "timestamp": a.timestamp.isoformat()
        } for a in appts
    ]

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
