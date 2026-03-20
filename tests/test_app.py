import pytest
import os
import sqlite3
from app.core.db import DatabaseManager
from app.core.config.settings import AppSettings
from PySide6.QtCore import QCoreApplication

# Notwendig für QSettings Tests ohne GUI-Eventloop
@pytest.fixture(scope="session", autouse=True)
def qapp():
    return QCoreApplication.instance() or QCoreApplication([])

def test_database_persistence():
    db_path = "test_chat.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = DatabaseManager(db_path)
    db.save_message(1, "user", "Hallo!")
    db.save_message(1, "assistant", "Hallo! Wie kann ich helfen?")
    
    history = db.load_chat(1)
    assert len(history) == 2
    assert history[0][0] == "user"
    assert history[0][1] == "Hallo!"
    assert history[1][0] == "assistant"
    
    os.remove(db_path)

def test_settings_storage():
    from app.core.config.settings_backend import InMemoryBackend
    backend = InMemoryBackend()
    settings = AppSettings(backend=backend)
    settings.theme = "dark"
    settings.theme_id = "dark_default"
    settings.model = "test-model"
    settings.temperature = 0.5
    settings.save()

    new_settings = AppSettings(backend=backend)
    assert new_settings.theme == "dark"
    assert new_settings.theme_id == "dark_default"
    assert new_settings.model == "test-model"
    assert new_settings.temperature == 0.5
