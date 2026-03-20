"""
Tests für Policy-spezifische Render-Budgets.

Jede Policy definiert feste Limits; keine dynamische Anpassung.
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_policies import ChatContextPolicy, resolve_limits_for_policy
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
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    infra._settings = AppSettings(backend)
    infra._settings.load()
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


def test_architecture_policy_limits():
    """ARCHITECTURE: größeres Budget (100/100/80/8)."""
    limits = resolve_limits_for_policy(ChatContextPolicy.ARCHITECTURE)
    assert limits.max_project_chars == 100
    assert limits.max_chat_chars == 100
    assert limits.max_topic_chars == 80
    assert limits.max_total_lines == 8


def test_debug_policy_limits():
    """DEBUG: extrem kleines Budget (60/60/40/4)."""
    limits = resolve_limits_for_policy(ChatContextPolicy.DEBUG)
    assert limits.max_project_chars == 60
    assert limits.max_chat_chars == 60
    assert limits.max_topic_chars == 40
    assert limits.max_total_lines == 4


def test_exploration_policy_limits():
    """EXPLORATION: mittleres Budget (80/80/60/6)."""
    limits = resolve_limits_for_policy(ChatContextPolicy.EXPLORATION)
    assert limits.max_project_chars == 80
    assert limits.max_chat_chars == 80
    assert limits.max_topic_chars == 60
    assert limits.max_total_lines == 6


def test_trace_contains_resolved_limits(services):
    """Trace enthält limits_source und aufgelöste Limit-Werte."""
    _, _, _, trace, _ = get_chat_service()._resolve_context_configuration(
        context_policy=ChatContextPolicy.ARCHITECTURE,
    )
    assert trace.limits_source == "policy"
    assert trace.max_project_chars == 100
    assert trace.max_chat_chars == 100
    assert trace.max_topic_chars == 80
    assert trace.max_total_lines == 8

    _, _, _, trace_default, _ = get_chat_service()._resolve_context_configuration()
    assert trace_default.limits_source == "default"
    assert trace_default.max_project_chars == 80
    assert trace_default.max_chat_chars == 80
    assert trace_default.max_topic_chars == 60
    assert trace_default.max_total_lines == 6
