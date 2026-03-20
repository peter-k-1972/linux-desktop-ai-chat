"""
Tests für Chat-Kontext-Resolution-Trace.

Jede gewählte Konfiguration muss nachvollziehbar sein.
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_policies import ChatContextPolicy
from app.chat.request_context_hints import RequestContextHint
from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode
from app.core.config.settings import AppSettings
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


@pytest.fixture
def services(temp_db, qapp):
    db = DatabaseManager(db_path=temp_db)
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


def test_trace_for_individual_settings(services):
    """individual_settings: source=individual_settings, profile=None."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    backend.setValue("chat_context_mode", "semantic")
    backend.setValue("chat_context_detail_level", "standard")
    backend.setValue("chat_context_include_project", True)
    backend.setValue("chat_context_include_chat", True)
    backend.setValue("chat_context_include_topic", False)
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    mode, detail, render_options, trace, _ = get_chat_service()._resolve_context_configuration()

    assert trace.source == "individual_settings"
    assert trace.profile is None
    assert trace.policy is None
    assert trace.hint is None
    assert trace.profile_enabled is False
    assert trace.mode == "semantic"
    assert trace.detail == "standard"
    assert mode == ChatContextMode.SEMANTIC
    assert detail == ChatContextDetailLevel.STANDARD


def test_trace_for_profile_resolution(services):
    """profile: source=profile, profile=balanced."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", True)
    backend.setValue("chat_context_profile", "balanced")
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    mode, detail, render_options, trace, _ = get_chat_service()._resolve_context_configuration()

    assert trace.source == "profile"
    assert trace.profile == "balanced"
    assert trace.profile_enabled is True
    assert trace.mode == "semantic"
    assert trace.detail == "standard"
    assert mode == ChatContextMode.SEMANTIC
    assert detail == ChatContextDetailLevel.STANDARD


def test_trace_for_request_hint_resolution(services):
    """request_hint: source=request_hint, profile=strict_minimal."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    mode, detail, render_options, trace, _ = get_chat_service()._resolve_context_configuration(
        request_context_hint=RequestContextHint.LOW_CONTEXT_QUERY
    )

    assert trace.source == "request_hint"
    assert trace.profile == "strict_minimal"
    assert trace.hint == "low_context_query"
    assert trace.profile_enabled is False
    assert trace.mode == "semantic"
    assert trace.detail == "minimal"
    assert mode == ChatContextMode.SEMANTIC
    assert detail == ChatContextDetailLevel.MINIMAL


def test_trace_lists_enabled_fields_correctly(services):
    """Trace enthält nur aktivierte Felder."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", True)
    backend.setValue("chat_context_profile", "strict_minimal")
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    _, _, _, trace, _ = get_chat_service()._resolve_context_configuration()

    assert trace.fields == ["project"]
    assert "chat" not in trace.fields
    assert "topic" not in trace.fields


def test_trace_with_policy(services):
    """Trace mit Policy: policy=architecture, hint=None, profile_enabled=false."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    _, _, _, trace, _ = get_chat_service()._resolve_context_configuration(
        request_context_hint=None,
        context_policy=ChatContextPolicy.ARCHITECTURE,
    )

    assert trace.source == "policy"
    assert trace.policy == "architecture"
    assert trace.hint is None
    assert trace.profile_enabled is False
    assert trace.profile == "full_guidance"
    assert trace.mode == "semantic"
    assert trace.detail == "full"
    assert trace.fields == ["project", "chat", "topic"]


def test_trace_precedence_chain(services):
    """Vollständige Kette: profile_enabled=True gewinnt trotz policy+hint."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", True)
    backend.setValue("chat_context_profile", "balanced")
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    _, _, _, trace, _ = get_chat_service()._resolve_context_configuration(
        request_context_hint=RequestContextHint.LOW_CONTEXT_QUERY,
        context_policy=ChatContextPolicy.ARCHITECTURE,
    )

    assert trace.source == "profile"
    assert trace.profile == "balanced"
    assert trace.profile_enabled is True
    assert trace.policy == "architecture"
    assert trace.hint == "low_context_query"
