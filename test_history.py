import pytest
from sqlalchemy import create_engine
from database import set_test_engine, init_db, log_interaction_db, get_user_history

@pytest.fixture
def setup_db(tmp_path):
    """Fixture to create a temporary database."""
    temp_db = tmp_path / "test_history.db"
    engine = create_engine(f"sqlite:///{temp_db}")
    set_test_engine(engine)
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
    # Each interaction log contains 2 messages (user + assistant)
    assert len(history) == 20
    # ordered by timestamp DESC in query, then reversed.
    # 10 newest are msg19...msg10. Reversed is msg10...msg19.
    assert "msg10" in history[0]["content"]
    assert "resp19" in history[-1]["content"]
