"""
Tests für Chat-Kontext-Feldsteuerung (include_project, include_chat, include_topic).

Reine Regelsteuerung, keine Heuristik.
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.core.config.settings import AppSettings, ChatContextDetailLevel, ChatContextMode
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.chat.context import (
    ChatContextRenderOptions,
    ChatRequestContext,
    inject_chat_context_into_messages,
)
from app.services.infrastructure import set_infrastructure, _ServiceInfrastructure


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
    db = DatabaseManager(db_path=temp_db)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = AppSettings()
    set_infrastructure(infra)
    from app.services.project_service import ProjectService
    from app.services.chat_service import ChatService
    from app.services.topic_service import TopicService
    from app.services.project_service import set_project_service
    from app.services.chat_service import set_chat_service
    from app.services.topic_service import set_topic_service
    set_project_service(ProjectService())
    set_chat_service(ChatService())
    set_topic_service(TopicService())
    yield
    set_project_service(None)
    set_chat_service(None)
    set_topic_service(None)
    set_infrastructure(None)


CTX = ChatRequestContext(
    project_name="XYZ",
    chat_title="Debug Session",
    topic_name="API",
)


def test_project_only_fragment():
    """Nur Projekt-Feld gerendert."""
    opts = ChatContextRenderOptions(include_project=True, include_chat=False, include_topic=False)
    frag = CTX.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
    )
    assert "Projekt: XYZ" in frag
    assert "Chat:" not in frag
    assert "Topic:" not in frag


def test_chat_only_fragment():
    """Nur Chat-Feld gerendert."""
    opts = ChatContextRenderOptions(include_project=False, include_chat=True, include_topic=False)
    frag = CTX.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
    )
    assert "Chat: Debug Session" in frag
    assert "Projekt:" not in frag
    assert "Topic:" not in frag


def test_topic_only_fragment():
    """Nur Topic-Feld gerendert."""
    opts = ChatContextRenderOptions(include_project=False, include_chat=False, include_topic=True)
    frag = CTX.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
    )
    assert "Topic: API" in frag
    assert "Projekt:" not in frag
    assert "Chat:" not in frag


def test_all_fields_disabled_returns_empty_fragment():
    """Alle Felder deaktiviert → leerer Fragment."""
    opts = ChatContextRenderOptions(
        include_project=False,
        include_chat=False,
        include_topic=False,
    )
    frag = CTX.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
    )
    assert frag == ""


def test_empty_fragment_skips_injection(services):
    """Leerer Fragment → keine Injection."""
    from app.services.chat_service import get_chat_service
    from app.services.project_service import get_project_service
    from app.services.infrastructure import get_infrastructure

    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    p1 = proj_svc.create_project("P", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "C", topic_id=None)

    settings = get_infrastructure().settings
    settings.chat_context_mode = "semantic"
    settings.chat_context_include_project = False
    settings.chat_context_include_chat = False
    settings.chat_context_include_topic = False
    settings.save()

    messages = [{"role": "user", "content": "Hallo"}]
    result = chat_svc._inject_chat_context(messages, cid)

    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert result == messages


def test_semantic_full_without_topic_still_valid():
    """SEMANTIC FULL ohne Topic-Feld bleibt gültig (Projekt + Chat)."""
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=False)
    frag = CTX.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC,
        ChatContextDetailLevel.FULL,
        opts,
    )
    assert "Arbeitskontext:" in frag
    assert "Projekt: XYZ (Themenbereich)" in frag
    assert "Chat: Debug Session (laufende Konversation)" in frag
    assert "Topic:" not in frag
    assert "Berücksichtige diesen Kontext" in frag
