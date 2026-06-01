
import pytest
import hashlib
from app import authenticate, register_user
from database import set_db_path, init_db, add_user

@pytest.fixture
def setup_db(tmp_path):
    """Fixture to create a temporary database."""
    temp_db = tmp_path / "test_university.db"
    set_db_path(temp_db)
    init_db()
    
    # Pre-register test admin
    add_user("test_admin", hashlib.sha256("admin123".encode()).hexdigest(), "admin")
    
    yield temp_db

def test_registration_success(setup_db):
    """Test successful user registration."""
    success, msg = register_user("new_user", "password123")
    assert success is True
    assert msg == "Account created!"

def test_registration_duplicate(setup_db):
    """Test registration with existing username."""
    success, msg = register_user("test_admin", "password123")
    assert success is False
    assert msg == "Username exists"

def test_authentication_success(setup_db):
    """Test successful authentication."""
    success, role = authenticate("test_admin", "admin123")
    assert success is True
    assert role == "admin"

def test_authentication_failure(setup_db):
    """Test authentication with wrong password."""
    success, role = authenticate("test_admin", "wrong_password")
    assert success is False
    assert role is None
