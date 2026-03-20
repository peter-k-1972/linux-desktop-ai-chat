"""
Regression: Chat ohne Projekt – Chat als Grundfunktion nutzbar.

Verifiziert:
- Start ohne Projekt: Chat-Service liefert globale Chats
- Chat öffnen ohne Projekt: list_chats_for_project(None) funktioniert
- Chat anlegen ohne Projekt: create_chat() erzeugt Chat ohne Projekt
- Projektgebundener Chat weiterhin funktionsfähig
"""

import os
import tempfile

import pytest

from app.core.db import DatabaseManager
from app.services.chat_service import get_chat_service
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.core.config.settings import AppSettings


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def chat_service_with_db(temp_db):
    """ChatService mit temporärer DB."""
    from app.services.chat_service import set_chat_service

    db = DatabaseManager(db_path=temp_db)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = AppSettings()
    set_infrastructure(infra)
    set_chat_service(None)
    yield get_chat_service(), db
    set_chat_service(None)
    set_infrastructure(None)


def test_create_chat_without_project(chat_service_with_db):
    """Neuer Chat kann ohne Projekt angelegt werden."""
    svc, _ = chat_service_with_db

    chat_id = svc.create_chat("Globaler Chat")
    assert chat_id > 0

    info = svc.get_chat_info(chat_id)
    assert info is not None
    assert info.get("title") == "Globaler Chat"


def test_list_chats_global_without_project(chat_service_with_db):
    """list_chats_for_project(None) liefert alle Chats (global)."""
    svc, db = chat_service_with_db

    c1 = svc.create_chat("Chat ohne Projekt")
    c2 = svc.create_chat("Zweiter globaler Chat")

    chats = svc.list_chats_for_project(None)
    assert len(chats) >= 2
    ids = {c.get("id") for c in chats}
    assert c1 in ids
    assert c2 in ids
    for c in chats:
        assert c.get("topic_id") is None
        assert c.get("topic_name") is None
        assert c.get("pinned") == 0
        assert c.get("archived") == 0
        assert "last_activity" in c or "created_at" in c


def test_chat_without_project_supports_messages(chat_service_with_db):
    """Chat ohne Projekt kann Nachrichten speichern und laden."""
    svc, _ = chat_service_with_db

    chat_id = svc.create_chat("Test")
    svc.save_message(chat_id, "user", "Hallo")
    svc.save_message(chat_id, "assistant", "Antwort")

    msgs = svc.load_chat(chat_id)
    assert len(msgs) == 2
    assert msgs[0][1] == "Hallo"
    assert msgs[1][1] == "Antwort"


def test_project_bound_chat_still_works(chat_service_with_db):
    """Projektgebundener Chat funktioniert weiterhin."""
    svc, db = chat_service_with_db

    p_id = db.create_project("Test Projekt")
    chat_id = svc.create_chat_in_project(p_id, "Projekt-Chat")

    chats = svc.list_chats_for_project(p_id)
    assert len(chats) == 1
    assert chats[0].get("id") == chat_id
    assert chats[0].get("title") == "Projekt-Chat"

    global_chats = svc.list_chats_for_project(None)
    ids = {c.get("id") for c in global_chats}
    assert chat_id in ids


def test_mixed_global_and_project_chats(chat_service_with_db):
    """Globale und projektgebundene Chats koexistieren."""
    svc, db = chat_service_with_db

    c_global = svc.create_chat("Global")
    p_id = db.create_project("Projekt")
    c_project = svc.create_chat_in_project(p_id, "Projekt-Chat")

    global_list = svc.list_chats_for_project(None)
    project_list = svc.list_chats_for_project(p_id)

    assert c_global in {c.get("id") for c in global_list}
    assert c_project in {c.get("id") for c in global_list}
    assert c_project in {c.get("id") for c in project_list}
    assert c_global not in {c.get("id") for c in project_list}


def test_global_filter_recent_days(chat_service_with_db):
    """Einfacher Filter: recent_days filtert globale Chats."""
    svc, _ = chat_service_with_db

    chat_id = svc.create_chat("Globaler Chat")
    all_chats = svc.list_chats_for_project(None)
    recent_chats = svc.list_chats_for_project(None, recent_days=7)

    assert chat_id in {c.get("id") for c in all_chats}
    assert chat_id in {c.get("id") for c in recent_chats}
