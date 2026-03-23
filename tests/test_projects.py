import pytest

from app.core.db import DatabaseManager


def test_project_crud(tmp_path):
    db_path = str(tmp_path / "test_projects.db")
    db = DatabaseManager(db_path, ensure_default_project=False)

    # Create
    p_id = db.create_project("Test Projekt")
    assert p_id > 0

    # List
    projects = db.list_projects()
    assert len(projects) == 1
    assert projects[0]["name"] == "Test Projekt"

    # Rename
    db.rename_project(p_id, "Umbenanntes Projekt")
    projects = db.list_projects()
    assert projects[0]["name"] == "Umbenanntes Projekt"

    # Filter
    projects = db.list_projects("Umbenannt")
    assert len(projects) == 1
    projects = db.list_projects("Nichts")
    assert len(projects) == 0

    # Delete
    db.delete_project(p_id)
    projects = db.list_projects()
    assert len(projects) == 0


def test_project_chat_assignment(tmp_path):
    db_path = str(tmp_path / "test_projects_chats.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    
    p_id = db.create_project("Projekt 1")
    c_id = db.create_chat("Chat 1")
    
    # Add
    db.add_chat_to_project(p_id, c_id)
    
    # Get project of chat
    assert db.get_project_of_chat(c_id) == p_id
    
    # List chats of project
    chats = db.list_chats_of_project(p_id)
    assert len(chats) == 1
    assert chats[0]["id"] == c_id
    assert chats[0]["title"] == "Chat 1"
    
    # Remove
    db.remove_chat_from_project(p_id, c_id)
    chats = db.list_chats_of_project(p_id)
    assert len(chats) == 0
    assert db.get_project_of_chat(c_id) is None


def test_project_update_clears_default_context_policy(tmp_path):
    db_path = str(tmp_path / "test_policy.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    pid = db.create_project("P", default_context_policy="debug")
    row = db.get_project(pid)
    assert row.get("default_context_policy") == "debug"

    db.update_project(pid, clear_default_context_policy=True)
    row2 = db.get_project(pid)
    assert row2.get("default_context_policy") is None


def test_list_projects_includes_default_context_policy(tmp_path):
    db_path = str(tmp_path / "test_list_pol.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    pid = db.create_project("P", default_context_policy="architecture")
    listed = db.list_projects()
    assert len(listed) == 1
    assert listed[0].get("project_id") == pid
    assert listed[0].get("default_context_policy") == "architecture"


def test_format_default_context_policy_caption():
    from app.projects.models import format_default_context_policy_caption

    assert "App-Standard" in format_default_context_policy_caption({"project_id": 1})
    assert "default" in format_default_context_policy_caption(
        {"default_context_policy": "default"}
    ).lower()
    assert "Gespeichert" in format_default_context_policy_caption(
        {"default_context_policy": "not_a_real_policy_xyz"}
    )
