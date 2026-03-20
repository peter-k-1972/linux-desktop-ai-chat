import pytest
import os
from app.core.db import DatabaseManager

def test_project_crud():
    db_path = "test_projects.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = DatabaseManager(db_path)
    
    # Create
    p_id = db.create_project("Test Projekt")
    assert p_id > 0
    
    # List
    projects = db.list_projects()
    assert len(projects) == 1
    assert projects[0][1] == "Test Projekt"
    
    # Rename
    db.rename_project(p_id, "Umbenanntes Projekt")
    projects = db.list_projects()
    assert projects[0][1] == "Umbenanntes Projekt"
    
    # Filter
    projects = db.list_projects("Umbenannt")
    assert len(projects) == 1
    projects = db.list_projects("Nichts")
    assert len(projects) == 0
    
    # Delete
    db.delete_project(p_id)
    projects = db.list_projects()
    assert len(projects) == 0
    
    if os.path.exists(db_path):
        os.remove(db_path)

def test_project_chat_assignment():
    db_path = "test_projects_chats.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = DatabaseManager(db_path)
    
    p_id = db.create_project("Projekt 1")
    c_id = db.create_chat("Chat 1")
    
    # Add
    db.add_chat_to_project(p_id, c_id)
    
    # Get project of chat
    assert db.get_project_of_chat(c_id) == p_id
    
    # List chats of project
    chats = db.list_chats_of_project(p_id)
    assert len(chats) == 1
    assert chats[0][0] == c_id
    assert chats[0][1] == "Chat 1"
    
    # Remove
    db.remove_chat_from_project(p_id, c_id)
    chats = db.list_chats_of_project(p_id)
    assert len(chats) == 0
    assert db.get_project_of_chat(c_id) is None
    
    if os.path.exists(db_path):
        os.remove(db_path)
