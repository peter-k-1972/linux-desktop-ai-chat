"""
Tests für Projekt-/Chat-/Workspace-Struktur.

Verifiziert:
- Projekte existieren und werden geladen
- Chats sind Projekten zuordenbar
- Projektwechsel aktualisiert Kontext (Service-Ebene)
- Chat-Listen / Projektlisten sind konsistent
"""

import os
import tempfile

import pytest

from app.core.db import DatabaseManager
from app.services.chat_service import get_chat_service, set_chat_service
from app.services.project_service import get_project_service, set_project_service
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
def services_with_db(temp_db):
    """ProjectService und ChatService mit temporärer DB."""
    db = DatabaseManager(db_path=temp_db)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = AppSettings()
    set_infrastructure(infra)
    set_chat_service(None)
    set_project_service(None)
    yield get_project_service(), get_chat_service(), db
    set_chat_service(None)
    set_project_service(None)
    set_infrastructure(None)


def test_projects_exist_and_load(services_with_db):
    """Projekte existieren und werden geladen."""
    proj_svc, _, db = services_with_db

    p1 = proj_svc.create_project("Projekt A")
    p2 = proj_svc.create_project("Projekt B")

    assert p1 > 0
    assert p2 > 0

    projects = proj_svc.list_projects()
    assert len(projects) >= 2
    names = {p.get("name") for p in projects}
    assert "Projekt A" in names
    assert "Projekt B" in names


def test_chats_assignable_to_projects(services_with_db):
    """Chats sind Projekten zuordenbar."""
    proj_svc, chat_svc, _ = services_with_db

    p_id = proj_svc.create_project("Test")
    chat_id = chat_svc.create_chat_in_project(p_id, "Projekt-Chat")

    assert chat_id > 0

    project_of_chat = proj_svc.get_project_of_chat(chat_id)
    assert project_of_chat == p_id

    chats = chat_svc.list_chats_for_project(p_id)
    assert len(chats) >= 1
    assert any(c.get("id") == chat_id for c in chats)


def test_project_switch_chat_list_consistency(services_with_db):
    """Projektwechsel: Chat-Listen sind pro Projekt getrennt."""
    proj_svc, chat_svc, _ = services_with_db

    p1 = proj_svc.create_project("Projekt 1")
    p2 = proj_svc.create_project("Projekt 2")

    c1 = chat_svc.create_chat_in_project(p1, "Chat in P1")
    c2 = chat_svc.create_chat_in_project(p2, "Chat in P2")
    c_global = chat_svc.create_chat("Globaler Chat")

    list_p1 = chat_svc.list_chats_for_project(p1)
    list_p2 = chat_svc.list_chats_for_project(p2)
    list_global = chat_svc.list_chats_for_project(None)

    ids_p1 = {c.get("id") for c in list_p1}
    ids_p2 = {c.get("id") for c in list_p2}
    ids_global = {c.get("id") for c in list_global}

    assert c1 in ids_p1
    assert c1 not in ids_p2
    assert c2 in ids_p2
    assert c2 not in ids_p1
    assert c_global in ids_global
    assert c1 in ids_global
    assert c2 in ids_global


def test_chat_list_no_regression(services_with_db):
    """Chat-Grundpfad: Liste, Laden, Speichern funktioniert."""
    _, chat_svc, _ = services_with_db

    chat_id = chat_svc.create_chat("Regression-Chat")
    assert chat_id > 0

    chats = chat_svc.list_chats_for_project(None)
    assert any(c.get("id") == chat_id for c in chats)

    chat_svc.save_message(chat_id, "user", "Test")
    chat_svc.save_message(chat_id, "assistant", "Antwort")

    msgs = chat_svc.load_chat(chat_id)
    assert len(msgs) == 2
