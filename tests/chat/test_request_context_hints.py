"""
Tests für Request-Context-Hints.

Explizite Hints vom Aufrufer. Keine automatische Klassifikation.
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_profiles import resolve_profile_for_request_hint
from app.chat.request_context_hints import RequestContextHint
from app.core.config.settings import ChatContextProfile
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, set_project_service
from app.services.topic_service import TopicService, set_topic_service


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


def test_general_question_maps_to_balanced():
    """general_question → balanced."""
    assert resolve_profile_for_request_hint(RequestContextHint.GENERAL_QUESTION) == ChatContextProfile.BALANCED


def test_architecture_work_maps_to_full_guidance():
    """architecture_work → full_guidance."""
    assert resolve_profile_for_request_hint(RequestContextHint.ARCHITECTURE_WORK) == ChatContextProfile.FULL_GUIDANCE


def test_topic_focus_maps_to_balanced():
    """topic_focus → balanced."""
    assert resolve_profile_for_request_hint(RequestContextHint.TOPIC_FOCUS) == ChatContextProfile.BALANCED


def test_low_context_query_maps_to_strict_minimal():
    """low_context_query → strict_minimal."""
    assert resolve_profile_for_request_hint(RequestContextHint.LOW_CONTEXT_QUERY) == ChatContextProfile.STRICT_MINIMAL


@pytest.fixture
def services(temp_db, qapp):
    db = DatabaseManager(db_path=temp_db)
    db.create_chat("Test Chat")
    db.create_project("Test Project")
    db.add_chat_to_project(1, 1, None)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = None
    set_infrastructure(infra)
    set_project_service(ProjectService())
    set_chat_service(ChatService())
    set_topic_service(TopicService())
    try:
        yield
    finally:
        set_project_service(None)
        set_chat_service(None)
        set_topic_service(None)
        set_infrastructure(None)


def test_hint_used_only_when_profile_disabled(services):
    """Hint wird nur genutzt wenn profile_enabled=False. Bei True wird Profil verwendet."""
    from app.core.config.settings import AppSettings

    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    backend.setValue("chat_context_mode", "semantic")
    backend.setValue("chat_context_detail_level", "full")
    backend.setValue("chat_context_include_project", True)
    backend.setValue("chat_context_include_chat", True)
    backend.setValue("chat_context_include_topic", True)
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    messages = [{"role": "user", "content": "Hello"}]
    result = get_chat_service()._inject_chat_context(
        messages, 1, request_context_hint=RequestContextHint.LOW_CONTEXT_QUERY
    )

    assert result != messages
    fragment = result[0].get("content", "")
    assert "Arbeitskontext:" in fragment
    assert "- Projekt:" in fragment
    assert "- Chat:" not in fragment
    assert "- Topic:" not in fragment


def test_without_hint_falls_back_to_individual_settings(services):
    """Ohne Hint und ohne Profil: Einzelsettings (mode=off) → keine Injektion."""
    from app.core.config.settings import AppSettings

    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    backend.setValue("chat_context_mode", "off")
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    messages = [{"role": "user", "content": "Hello"}]
    result = get_chat_service()._inject_chat_context(messages, 1, request_context_hint=None)

    assert result == messages
