"""
Tests für Chat-Kontext-Aktionen.

Verifiziert:
- Chat verschieben → Kontext korrekt
- Topic ändern → Kontext korrekt
- Neuer Chat → korrektes Projekt
- Keine Kontext-Leaks
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.core.db.database_manager import DatabaseManager
from app.services.project_service import get_project_service, set_project_service
from app.services.chat_service import get_chat_service, set_chat_service
from app.services.topic_service import get_topic_service, set_topic_service
from app.services.infrastructure import set_infrastructure, _ServiceInfrastructure
from app.core.config.settings import AppSettings


def _ensure_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


@pytest.fixture
def temp_db():
    """Temporäre SQLite-DB – DatabaseManager erstellt Schema."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        yield path
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


@pytest.fixture
def services(temp_db, qapp):
    """Initialisierte Services mit temp DB."""
    db = DatabaseManager(db_path=temp_db)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = AppSettings()
    set_infrastructure(infra)
    set_project_service(None)
    set_chat_service(None)
    set_topic_service(None)
    from app.services.project_service import ProjectService
    from app.services.chat_service import ChatService
    from app.services.topic_service import TopicService
    set_project_service(ProjectService())
    set_chat_service(ChatService())
    set_topic_service(TopicService())
    yield
    set_project_service(None)
    set_chat_service(None)
    set_topic_service(None)
    set_infrastructure(None)


def test_move_chat_to_project(services):
    """Chat verschieben: remove + add, Kontext korrekt."""
    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    db = proj_svc._infra.database

    p1 = proj_svc.create_project("Projekt A", "", "active")
    p2 = proj_svc.create_project("Projekt B", "", "active")
    cid = chat_svc.create_chat("Chat 1")
    db.add_chat_to_project(p1, cid)

    assert proj_svc.get_project_of_chat(cid) == p1

    proj_svc.move_chat_to_project(cid, p2)
    assert proj_svc.get_project_of_chat(cid) == p2


def test_move_global_chat_to_project(services):
    """Globaler Chat zu Projekt hinzufügen."""
    proj_svc = get_project_service()
    chat_svc = get_chat_service()

    p1 = proj_svc.create_project("Projekt A", "", "active")
    cid = chat_svc.create_chat("Globaler Chat")

    assert proj_svc.get_project_of_chat(cid) is None

    proj_svc.move_chat_to_project(cid, p1)
    assert proj_svc.get_project_of_chat(cid) == p1


def test_topic_change_updates_context(services):
    """Topic ändern → get_chat_info liefert neues Topic."""
    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    topic_svc = get_topic_service()

    p1 = proj_svc.create_project("Projekt", "", "active")
    t1 = topic_svc.create_topic(p1, "Topic A", "")
    t2 = topic_svc.create_topic(p1, "Topic B", "")
    cid = chat_svc.create_chat_in_project(p1, "Chat", topic_id=t1)

    info = chat_svc.get_chat_info(cid)
    assert info.get("topic_id") == t1
    assert "Topic A" in (info.get("topic_name") or "")

    chat_svc.move_chat_to_topic(p1, cid, t2)
    info = chat_svc.get_chat_info(cid)
    assert info.get("topic_id") == t2
    assert "Topic B" in (info.get("topic_name") or "")


def test_new_chat_in_project_context(services):
    """Neuer Chat im Projekt-Kontext hat korrektes Projekt."""
    proj_svc = get_project_service()
    chat_svc = get_chat_service()

    p1 = proj_svc.create_project("Projekt", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "Neuer Chat")

    assert proj_svc.get_project_of_chat(cid) == p1
    info = chat_svc.get_chat_info(cid)
    assert info.get("title") == "Neuer Chat"


def test_context_bar_signals(qapp):
    """ContextBar emittiert project_clicked, chat_clicked, topic_clicked."""
    from app.gui.domains.operations.chat.panels.chat_context_bar import ChatContextBar

    bar = ChatContextBar()
    bar.set_context(project_name="P", chat_title="C", topic_name="T")

    clicked = []

    def on_proj():
        clicked.append("project")

    def on_chat():
        clicked.append("chat")

    def on_topic():
        clicked.append("topic")

    bar.project_clicked.connect(on_proj)
    bar.chat_clicked.connect(on_chat)
    bar.topic_clicked.connect(on_topic)

    bar._project_label.click()
    assert "project" in clicked

    bar._chat_label.click()
    assert "chat" in clicked

    bar._topic_label.click()
    assert "topic" in clicked
