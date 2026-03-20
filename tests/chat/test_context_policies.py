"""
Tests für Chat-Kontext-Policies.

Use-Case-Zuordnung: explizit, regelbasiert, keine Heuristik.
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_policies import ChatContextPolicy, resolve_profile_for_policy
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


def test_policy_architecture_maps_to_full_guidance():
    """ARCHITECTURE → full_guidance."""
    assert resolve_profile_for_policy(ChatContextPolicy.ARCHITECTURE) == ChatContextProfile.FULL_GUIDANCE


def test_policy_debug_maps_to_strict_minimal():
    """DEBUG → strict_minimal."""
    assert resolve_profile_for_policy(ChatContextPolicy.DEBUG) == ChatContextProfile.STRICT_MINIMAL


def test_policy_exploration_maps_to_balanced():
    """EXPLORATION → balanced."""
    assert resolve_profile_for_policy(ChatContextPolicy.EXPLORATION) == ChatContextProfile.BALANCED


def test_policy_used_when_profile_disabled(services):
    """Policy wird genutzt wenn profile_enabled=False."""
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

    mode, detail, render_options, trace, _ = get_chat_service()._resolve_context_configuration(
        request_context_hint=None,
        context_policy=ChatContextPolicy.DEBUG,
    )

    assert trace.source == "policy"
    assert trace.profile == "strict_minimal"
    assert detail.value == "minimal"
    assert render_options.include_project is True
    assert render_options.include_chat is False
    assert render_options.include_topic is False


def test_policy_overridden_by_profile_enabled(services):
    """profile_enabled=True: Policy wird ignoriert, Settings-Profil gewinnt."""
    from app.core.config.settings import AppSettings

    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", True)
    backend.setValue("chat_context_profile", "full_guidance")
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    mode, detail, render_options, trace, _ = get_chat_service()._resolve_context_configuration(
        request_context_hint=None,
        context_policy=ChatContextPolicy.DEBUG,
    )

    assert trace.source == "profile"
    assert trace.profile == "full_guidance"
    assert detail.value == "full"


def test_policy_precedence_over_request_hint(services):
    """Policy hat Vorrang vor Request-Hint."""
    from app.core.config.settings import AppSettings

    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    mode, detail, render_options, trace, _ = get_chat_service()._resolve_context_configuration(
        request_context_hint=RequestContextHint.LOW_CONTEXT_QUERY,
        context_policy=ChatContextPolicy.ARCHITECTURE,
    )

    assert trace.source == "policy"
    assert trace.profile == "full_guidance"
    assert detail.value == "full"
