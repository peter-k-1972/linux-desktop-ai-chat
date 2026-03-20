"""
Regression: Einzelner Chat löschen – nur genau dieser wird entfernt.

Reproduziert und verhindert den Bug: Beim Löschen eines Chats aus der Sidebar
dürfen keine anderen Chats gelöscht werden; die Chatliste muss korrekt
aktualisiert werden.
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
    """ChatService mit temporärer DB und Projekt."""
    from app.services.chat_service import set_chat_service

    db = DatabaseManager(db_path=temp_db)
    p_id = db.create_project("Test Projekt")
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = AppSettings()
    set_infrastructure(infra)
    set_chat_service(None)
    yield get_chat_service(), db, p_id
    set_chat_service(None)
    set_infrastructure(None)


def test_delete_single_chat_leaves_others_intact(chat_service_with_db):
    """
    Erzeuge mehrere Chats, lösche genau einen, verifiziere dass nur dieser
    entfernt wurde.
    """
    svc, db, project_id = chat_service_with_db

    c1 = svc.create_chat_in_project(project_id, "Chat 1")
    c2 = svc.create_chat_in_project(project_id, "Chat 2")
    c3 = svc.create_chat_in_project(project_id, "Chat 3")

    assert c1 != c2 != c3
    chats_before = svc.list_chats_for_project(project_id)
    assert len(chats_before) == 3
    ids_before = {c.get("id") for c in chats_before}
    assert ids_before == {c1, c2, c3}

    svc.delete_chat(c2)

    chats_after = svc.list_chats_for_project(project_id)
    assert len(chats_after) == 2
    ids_after = {c.get("id") for c in chats_after}
    assert ids_after == {c1, c3}
    assert c2 not in ids_after


def test_delete_chat_removes_messages_only_for_that_chat(chat_service_with_db):
    """Nachrichten anderer Chats bleiben erhalten."""
    svc, db, project_id = chat_service_with_db

    c1 = svc.create_chat_in_project(project_id, "Chat A")
    c2 = svc.create_chat_in_project(project_id, "Chat B")

    svc.save_message(c1, "user", "Nachricht in Chat A")
    svc.save_message(c2, "user", "Nachricht in Chat B")

    svc.delete_chat(c1)

    msgs_c1 = svc.load_chat(c1)
    msgs_c2 = svc.load_chat(c2)

    assert len(msgs_c1) == 0
    assert len(msgs_c2) == 1
    assert msgs_c2[0][1] == "Nachricht in Chat B"


def test_delete_chat_rejects_invalid_id(chat_service_with_db):
    """delete_chat mit ungültiger ID löscht nichts."""
    svc, db, project_id = chat_service_with_db

    c1 = svc.create_chat_in_project(project_id, "Chat 1")
    chats_before = svc.list_chats_for_project(project_id)
    assert len(chats_before) == 1

    svc.delete_chat(0)
    svc.delete_chat(-1)
    svc.delete_chat(None)

    chats_after = svc.list_chats_for_project(project_id)
    assert len(chats_after) == 1
    assert chats_after[0].get("id") == c1
