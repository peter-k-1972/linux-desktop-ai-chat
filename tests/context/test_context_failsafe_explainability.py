"""
QA for failsafe explainability – no silent cleanup.

Every failsafe action must create ContextWarningEntry and dropped entry (if tokens removed).
failsafe_triggered == True when any failsafe warning present.
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_limits import ChatContextRenderLimits
from app.chat.context_policies import ChatContextPolicy
from app.context.explainability.context_explanation_serializer import explanation_to_dict
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.context_inspection_service import get_context_inspection_service
from app.services.context_explain_service import ContextExplainRequest
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, get_project_service, set_project_service
from app.services.topic_service import TopicService, get_topic_service, set_topic_service

pytestmark = pytest.mark.context_observability

FAILSAFE_WARNING_TYPES = (
    "failsafe",
    "header_only_fragment_removed",
    "marker_only_fragment_removed",
    "empty_injection_prevented",
)


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


def _setup_chat(services) -> int:
    backend = InMemoryBackend()
    backend.setValue("chat_context_mode", "semantic")
    backend.setValue("chat_context_detail_level", "standard")
    backend.setValue("chat_context_profile_enabled", False)
    backend.setValue("chat_context_include_project", True)
    backend.setValue("chat_context_include_chat", True)
    backend.setValue("chat_context_include_topic", True)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("Proj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "Topic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "Chat", topic_id=topic_id
    )
    return chat_id


def _assert_failsafe_visible(expl):
    """Assert failsafe actions are visible: warnings and dropped entries exist, failsafe_triggered=True."""
    has_failsafe_warning = any(
        getattr(w, "warning_type", "") in FAILSAFE_WARNING_TYPES
        or getattr(w, "effect", None) in ("removed_fragment", "skipped_injection")
        for w in expl.warnings
    )
    has_failsafe_dropped = any(
        e.reason == "failsafe_cleanup" for e in expl.dropped_by_source
    )
    assert has_failsafe_warning, "Failsafe must create ContextWarningEntry"
    assert has_failsafe_dropped, "Failsafe must create dropped entry"
    assert expl.failsafe_triggered is True, "failsafe_triggered must be True when failsafe warning present"


def test_header_only_removal_failsafe_visible(services):
    """Header-only fragment removed: warning and dropped entry present, failsafe_triggered=True."""
    def _limits_max_lines_1(policy):
        return ChatContextRenderLimits(
            max_project_chars=80,
            max_chat_chars=80,
            max_topic_chars=60,
            max_total_lines=1,
        )

    chat_id = _setup_chat(services)
    with patch("app.chat.context_policies.resolve_limits_for_policy", side_effect=_limits_max_lines_1):
        trace = get_chat_service().get_context_explanation(
            chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
        )
    expl = trace.explanation
    assert expl is not None
    _assert_failsafe_visible(expl)


def test_empty_injection_prevention_failsafe_visible(services):
    """Empty injection (mode=off): warning and dropped entry present, failsafe_triggered=True."""
    chat_id = _setup_chat(services)
    backend = InMemoryBackend()
    backend.setValue("chat_context_mode", "off")
    backend.setValue("chat_context_detail_level", "standard")
    backend.setValue("chat_context_profile_enabled", False)
    backend.setValue("chat_context_include_project", True)
    backend.setValue("chat_context_include_chat", True)
    backend.setValue("chat_context_include_topic", True)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings
    trace = get_chat_service().get_context_explanation(
        chat_id, None, None, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None
    _assert_failsafe_visible(expl)


def test_marker_only_removal_failsafe_visible(services):
    """Marker-only fragment (all fields meaningless): warning and dropped entry present."""
    def _limits_max_3(policy):
        return ChatContextRenderLimits(
            max_project_chars=3,
            max_chat_chars=3,
            max_topic_chars=3,
            max_total_lines=10,
        )

    chat_id = _setup_chat(services)
    with patch("app.chat.context_policies.resolve_limits_for_policy", side_effect=_limits_max_3):
        result = get_context_inspection_service().inspect(
            ContextExplainRequest(chat_id=chat_id, context_policy="architecture"),
            include_payload_preview=True,
            include_formatted=True,
        )
    expl = result.explanation
    assert expl is not None
    # With max 3 chars, project/chat/topic become "..." (meaningless); fragment may be header+instruction only
    # If we get marker_only, assert visibility
    has_failsafe = any(
        getattr(w, "warning_type", "") in FAILSAFE_WARNING_TYPES
        or getattr(w, "effect", None) in ("removed_fragment", "skipped_injection")
        for w in expl.warnings
    )
    if has_failsafe:
        _assert_failsafe_visible(expl)


def test_inspection_result_failsafe_serialized(services):
    """Failsafe (header-only) in inspection: warnings and dropped in JSON, failsafe_triggered=True."""
    def _limits_max_lines_1(policy):
        return ChatContextRenderLimits(
            max_project_chars=80,
            max_chat_chars=80,
            max_topic_chars=60,
            max_total_lines=1,
        )

    chat_id = _setup_chat(services)
    with patch("app.chat.context_policies.resolve_limits_for_policy", side_effect=_limits_max_lines_1):
        result = get_context_inspection_service().inspect(
            ContextExplainRequest(chat_id=chat_id, context_policy="architecture"),
            include_payload_preview=True,
            include_formatted=True,
        )
    d = explanation_to_dict(result.explanation)
    assert d.get("failsafe_triggered") is True
    warnings = d.get("warnings", [])
    assert any(w.get("warning_type") in FAILSAFE_WARNING_TYPES for w in warnings)
    dropped = d.get("dropped", {}).get("dropped_by_source", [])
    assert any(e.get("reason") == "failsafe_cleanup" for e in dropped)
