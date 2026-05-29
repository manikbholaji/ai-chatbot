import pytest
import json
import hashlib
from app import authenticate, register_user, load_users, save_users, USERS_FILE

@pytest.fixture
def setup_users(tmp_path):
    """Fixture to create a temporary users file."""
    temp_users_file = tmp_path / "users.json"
    
    # Mock USERS_FILE to use the temp one
    original_file = USERS_FILE
    import app
    app.USERS_FILE = temp_users_file
    
    # Initial data
    initial_data = {
        "test_admin": {
            "password": hashlib.sha256("admin123".encode()).hexdigest(),
            "role": "admin"
        }
    }
    with open(temp_users_file, "w") as f:
        json.dump(initial_data, f)
        
    yield temp_users_file
    
    # Restore original file path
    app.USERS_FILE = original_file

def test_registration_success(setup_users):
    """Test successful user registration."""
    success, msg = register_user("new_user", "password123")
    assert success is True
    assert msg == "Account created!"
    
    users = load_users()
    assert "new_user" in users
    assert users["new_user"]["role"] == "student"

def test_registration_duplicate(setup_users):
    """Test registration with existing username."""
    success, msg = register_user("test_admin", "password123")
    assert success is False
    assert msg == "Username exists"

def test_authentication_success(setup_users):
    """Test successful authentication."""
    success, role = authenticate("test_admin", "admin123")
    assert success is True
    assert role == "admin"

def test_authentication_failure(setup_users):
    """Test authentication with wrong password."""
    success, role = authenticate("test_admin", "wrong_password")
    assert success is False
    assert role is None

def test_authentication_nonexistent_user(setup_users):
    """Test authentication for a user that doesn't exist."""
    success, role = authenticate("non_existent", "password123")
    assert success is False
    assert role is None

def test_authentication_missing_role_fallback(setup_users):
    """Test authentication with missing role key (fallback to student)."""
    users = load_users()
    users["no_role_user"] = {
        "password": hashlib.sha256("password123".encode()).hexdigest()
    }
    save_users(users)
    
    success, role = authenticate("no_role_user", "password123")
    assert success is True
    assert role == "student"
