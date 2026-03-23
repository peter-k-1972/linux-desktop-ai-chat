"""Metadaten: zuletzt gespeicherter Agent pro Chat (messages.agent)."""

from app.core.db import DatabaseManager


def test_get_last_assistant_agent_for_chat_none_when_empty(tmp_path):
    db_path = str(tmp_path / "agents.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    cid = db.create_chat("c")
    assert db.get_last_assistant_agent_for_chat(cid) is None
    db.save_message(cid, "user", "hi", model=None, agent=None)
    assert db.get_last_assistant_agent_for_chat(cid) is None


def test_get_last_assistant_agent_for_chat_prefers_latest_with_agent(tmp_path):
    db_path = str(tmp_path / "agents2.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    cid = db.create_chat("c")
    db.save_message(cid, "assistant", "a", model="m", agent="planner-1")
    assert db.get_last_assistant_agent_for_chat(cid) == "planner-1"
    db.save_message(cid, "assistant", "b", model="m", agent=None)
    assert db.get_last_assistant_agent_for_chat(cid) == "planner-1"
    db.save_message(cid, "assistant", "c", model="m", agent="runner-2")
    assert db.get_last_assistant_agent_for_chat(cid) == "runner-2"
