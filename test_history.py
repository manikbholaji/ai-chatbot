import pytest
from app import load_recent_history
import json
import os

def test_load_recent_history_empty(tmp_path):
    """Test loading history from non-existent file."""
    import app
    original_log = app.project_path("data", "interaction_logs.jsonl")
    
    # Mock log file path to a non-existent one
    temp_log = tmp_path / "missing_logs.jsonl"
    
    # We need to mock the project_path return or similar
    # For simplicity, let's just use the real function if we can control the environment
    # But load_recent_history has a hardcoded path based on project_path
    
    # Let's try to pass the username and see it returns [] if file doesn't exist
    # Note: load_recent_history uses project_path("data", "interaction_logs.jsonl")
    # We might need to monkeypatch it.
    
def test_load_recent_history_filtering(tmp_path, monkeypatch):
    """Test that history is correctly filtered and limited by username."""
    temp_log_dir = tmp_path / "data"
    temp_log_dir.mkdir()
    temp_log_file = temp_log_dir / "interaction_logs.jsonl"
    
    # Sample data
    logs = [
        {"user": "user1", "student_message": "hi1", "bot_response": "hello1"},
        {"user": "user2", "student_message": "hi2", "bot_response": "hello2"},
        {"user": "user1", "student_message": "hi3", "bot_response": "hello3"},
    ]
    
    with open(temp_log_file, "w") as f:
        for entry in logs:
            f.write(json.dumps(entry) + "\n")
            
    # Monkeypatch project_path to return our temp path
    import app
    monkeypatch.setattr(app, "project_path", lambda *parts: tmp_path.joinpath(*parts))
    
    history = load_recent_history("user1", limit=10)
    assert len(history) == 4 # 2 turns * 2 (user + assistant)
    assert history[0]["content"] == "hi1"
    assert history[1]["content"] == "hello1"
    assert history[2]["content"] == "hi3"
    assert history[3]["content"] == "hello3"

def test_load_recent_history_limit(tmp_path, monkeypatch):
    """Test that history is limited correctly."""
    temp_log_dir = tmp_path / "data"
    temp_log_dir.mkdir()
    temp_log_file = temp_log_dir / "interaction_logs.jsonl"
    
    with open(temp_log_file, "w") as f:
        for i in range(20):
            entry = {"user": "user1", "student_message": f"msg{i}", "bot_response": f"resp{i}"}
            f.write(json.dumps(entry) + "\n")
            
    import app
    monkeypatch.setattr(app, "project_path", lambda *parts: tmp_path.joinpath(*parts))
    
    history = load_recent_history("user1", limit=10)
    assert len(history) == 10 # 5 turns * 2
    assert history[0]["content"] == "msg15"
    assert history[-1]["content"] == "resp19"
