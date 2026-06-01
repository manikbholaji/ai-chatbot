
import pytest
from database import set_db_path, init_db, log_interaction_db, get_user_history

@pytest.fixture
def setup_db(tmp_path):
    """Fixture to create a temporary database."""
    temp_db = tmp_path / "test_history.db"
    set_db_path(temp_db)
    init_db()
    yield temp_db

def test_load_recent_history_filtering(setup_db):
    """Test that history is correctly filtered and limited by username."""
    log_interaction_db("user1", "test", "hi1", "hello1", 0.0)
    log_interaction_db("user2", "test", "hi2", "hello2", 0.0)
    log_interaction_db("user1", "test", "hi3", "hello3", 0.0)
    
    history = get_user_history("user1", limit=10)
    assert len(history) == 4 # 2 turns * 2 (user + assistant)
    assert history[0]["content"] == "hi1"
    assert history[1]["content"] == "hello1"
    assert history[2]["content"] == "hi3"
    assert history[3]["content"] == "hello3"

def test_load_recent_history_limit(setup_db):
    """Test that history is limited correctly."""
    for i in range(20):
        log_interaction_db("user1", "test", f"msg{i}", f"resp{i}", 0.0)
            
    history = get_user_history("user1", limit=10)
    # limit=10 means 5 turns (each turn is 2 messages)
    assert len(history) == 10
    # ordered by timestamp ASC in return, but DESC in query.
    # Actually get_user_history returns reversed(logs).
    # Logs were DESC (newest first). 10 newest are msg19 to msg15.
    # Reversed(msg19..msg15) is msg15..msg19.
    assert "msg15" in history[0]["content"]
    assert "resp19" in history[-1]["content"]
