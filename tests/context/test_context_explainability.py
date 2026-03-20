"""
Tests für Kontext-Explainability.

Nutzt echten Resolver, kein Mocking der Explanation.
"""

import os
import tempfile
from pathlib import Path

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_policies import ChatContextPolicy
from app.chat.request_context_hints import RequestContextHint
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.context.debug.context_debug import format_context_explanation
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, get_project_service, set_project_service
from app.services.topic_service import TopicService, get_topic_service, set_topic_service

from tests.context.conftest import assert_snapshot

pytestmark = pytest.mark.context_observability


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


def _apply_settings(backend: InMemoryBackend, *, mode: str = "semantic", profile_enabled: bool = False):
    """Apply settings for consistent test context."""
    backend.setValue("chat_context_mode", mode)
    backend.setValue("chat_context_detail_level", "standard")
    backend.setValue("chat_context_profile_enabled", profile_enabled)
    backend.setValue("chat_context_include_project", True)
    backend.setValue("chat_context_include_chat", True)
    backend.setValue("chat_context_include_topic", True)


def test_explanation_exists(services):
    """Explanation wird vom Resolver zurückgegeben."""
    backend = InMemoryBackend()
    _apply_settings(backend, profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("ExplainProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "ExplainTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "ExplainChat", topic_id=topic_id
    )

    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    assert explanation is not None
    assert hasattr(explanation, "sources")
    assert hasattr(explanation, "decisions")
    assert hasattr(explanation, "compressions")
    assert hasattr(explanation, "warnings")


def test_decisions_logged(services):
    """Decisions werden korrekt geloggt."""
    backend = InMemoryBackend()
    _apply_settings(backend, profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("ExplainProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "ExplainTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "ExplainChat", topic_id=topic_id
    )

    explanation = get_chat_service().get_context_explanation(
        chat_id, RequestContextHint.LOW_CONTEXT_QUERY, ChatContextPolicy.ARCHITECTURE
    )

    decision_types = {d.decision_type for d in explanation.decisions}
    assert "policy" in decision_types
    assert "profile" in decision_types
    assert "field" in decision_types

    policy_dec = next(
        (d for d in explanation.decisions if d.decision_type == "policy"), None
    )
    assert policy_dec is not None
    assert policy_dec.outcome == "architecture"


def test_compression_visible(services):
    """Compression-Einträge sind sichtbar."""
    backend = InMemoryBackend()
    _apply_settings(backend, profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("ExplainProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "ExplainTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "ExplainChat", topic_id=topic_id
    )

    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    assert len(explanation.compressions) >= 1
    comp = explanation.compressions[0]
    assert comp.operation == "truncate"
    assert comp.original_chars is not None
    assert comp.final_chars is not None
    assert comp.before_tokens is not None
    assert comp.after_tokens is not None


def test_sources_token_accounting_correct(services):
    """Sources-Token-Accounting: chars_before/chars_after stimmen mit Identifier überein."""
    backend = InMemoryBackend()
    _apply_settings(backend, profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("ExplainProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "ExplainTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "ExplainChat", topic_id=topic_id
    )

    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    for src in explanation.sources:
        if src.identifier:
            assert src.chars_before is not None
            assert src.chars_before == len(src.identifier)
            assert src.chars_after is not None
            assert src.chars_after <= src.chars_before or src.chars_after <= 80
        assert src.selection_order is not None
        assert src.budget_allocated is not None
        assert src.budget_used is not None
        assert src.budget_dropped is not None


def test_source_budget_exhausted_when_line_limit_cuts_topic(services):
    """Topic: included=False, reason=budget_exhausted wenn Fragment Topic nicht enthält."""
    from app.chat.context import ChatContextRenderOptions, ChatRequestContext
    from app.chat.context_limits import ChatContextRenderLimits
    from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode
    from app.services.chat_service import _build_context_sources

    ctx = ChatRequestContext(
        project_name="Proj",
        chat_title="Chat",
        topic_name="Topic",
    )
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=True)
    limits = ChatContextRenderLimits(
        max_project_chars=80, max_chat_chars=80, max_topic_chars=60, max_total_lines=3
    )
    fragment = ctx.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC, ChatContextDetailLevel.STANDARD, opts, limits
    )
    assert "- Topic:" not in fragment
    sources = _build_context_sources(fragment, ctx, opts, limits)
    topic_src = next(s for s in sources if s.source_type == "topic")
    assert topic_src.included is False
    assert topic_src.reason == "budget_exhausted"
    assert topic_src.budget_used == 0
    assert topic_src.budget_dropped == 5


def test_dropped_context_report_with_profile_restriction(services):
    """Profile restriction: dropped_by_source and dropped_reasons populated."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", True)
    backend.setValue("chat_context_profile", "strict_minimal")
    settings = AppSettings(backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("ExplainProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "ExplainTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "ExplainChat", topic_id=topic_id
    )

    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    assert "profile_restriction" in explanation.dropped_reasons
    assert len(explanation.dropped_by_source) >= 2
    chat_dropped = next(
        (e for e in explanation.dropped_by_source if e.source_type == "chat"), None
    )
    assert chat_dropped is not None
    assert chat_dropped.reason == "profile_restriction"
    assert explanation.dropped_total_tokens is not None


def test_source_truncated_to_budget_when_char_limit_applied(services):
    """Project: reason=truncated_to_budget wenn max_project_chars kürzt."""
    from app.chat.context import ChatContextRenderOptions, ChatRequestContext
    from app.chat.context_limits import ChatContextRenderLimits
    from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode
    from app.services.chat_service import _build_context_sources

    ctx = ChatRequestContext(
        project_name="A" * 100,
        chat_title="Chat",
        topic_name="Topic",
    )
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=True)
    limits = ChatContextRenderLimits(
        max_project_chars=15, max_chat_chars=80, max_topic_chars=60, max_total_lines=10
    )
    fragment = ctx.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC, ChatContextDetailLevel.STANDARD, opts, limits
    )
    sources = _build_context_sources(fragment, ctx, opts, limits)
    proj_src = next(s for s in sources if s.source_type == "project")
    assert proj_src.included is True
    assert proj_src.reason == "truncated_to_budget"
    assert proj_src.chars_before == 100
    assert proj_src.chars_after == 15
    assert proj_src.budget_used == 15
    assert proj_src.budget_dropped == 85


def test_failsafe_warnings_logged(services):
    """Fail-Safe-Warnungen werden geloggt (mode=off)."""
    backend = InMemoryBackend()
    _apply_settings(backend, mode="off", profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("ExplainProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "ExplainTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "ExplainChat", topic_id=topic_id
    )

    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    assert len(explanation.warnings) >= 1
    failsafe_types = (
        "failsafe",
        "empty_injection_prevented",
        "header_only_fragment_removed",
        "marker_only_fragment_removed",
    )
    failsafe_warns = [
        w
        for w in explanation.warnings
        if w.warning_type in failsafe_types or getattr(w, "effect", None) == "skipped_injection"
    ]
    assert len(failsafe_warns) >= 1, "expected at least one failsafe warning"
    assert "mode=off" in failsafe_warns[0].message
    assert failsafe_warns[0].effect == "skipped_injection"
    assert explanation.warning_count == len(explanation.warnings)
    assert explanation.failsafe_triggered is True


def test_failsafe_structured_warning_fields(services):
    """Failsafe warnings include effect, warning_count, failsafe_triggered."""
    backend = InMemoryBackend()
    _apply_settings(backend, mode="off", profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("P", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "T", "")
    chat_id = get_chat_service().create_chat_in_project(proj_id, "C", topic_id=topic_id)

    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    assert explanation.warning_count >= 1
    assert explanation.failsafe_triggered is True
    failsafe_w = next(
        (w for w in explanation.warnings if getattr(w, "effect", None) == "skipped_injection"),
        None,
    )
    assert failsafe_w is not None
    assert failsafe_w.warning_type == "empty_injection_prevented"


def test_empty_result_markers_mode_off(services):
    """Empty-result markers set for mode=off: empty_result=True, empty_result_reason=disabled_mode."""
    backend = InMemoryBackend()
    _apply_settings(backend, mode="off", profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("P", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "T", "")
    chat_id = get_chat_service().create_chat_in_project(proj_id, "C", topic_id=topic_id)

    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    assert explanation.empty_result is True
    assert explanation.empty_result_reason == "disabled_mode"
    assert explanation.resolved_settings
    assert explanation.warnings


def test_empty_result_explanation_complete(services):
    """Empty-result explanation still contains resolved_settings, budget, warnings, reason."""
    from app.context.explainability.context_explanation_serializer import explanation_to_dict

    backend = InMemoryBackend()
    _apply_settings(backend, mode="off", profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("P", "", "active")
    chat_id = get_chat_service().create_chat_in_project(proj_id, "C", topic_id=None)

    explanation = get_chat_service().get_context_explanation(chat_id, None, None)
    d = explanation_to_dict(explanation)

    assert d["empty_result"] is True
    assert d["empty_result_reason"] == "disabled_mode"
    assert "resolved_settings" in d
    assert d["resolved_settings"]
    assert "budget" in d
    assert d["warnings"]


def test_trace_explanation_always_attached_when_return_trace_true(services):
    """When return_trace=True, trace.explanation is never None for any resolver exit path."""
    svc = get_chat_service()

    # Path 1: mode=off (early return)
    backend1 = InMemoryBackend()
    _apply_settings(backend1, mode="off", profile_enabled=False)
    settings1 = AppSettings(backend=backend1)
    settings1.load()
    svc._infra._settings = settings1
    proj_id = get_project_service().create_project("P", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "T", "")
    chat_id = svc.create_chat_in_project(proj_id, "C", topic_id=topic_id)
    result1 = svc.get_context_explanation(chat_id, None, None, return_trace=True)
    assert result1 is not None
    assert result1.explanation is not None, "mode=off path must attach explanation"
    assert hasattr(result1.explanation, "empty_result")
    assert result1.explanation.empty_result is True

    # Path 2: empty context (context.is_empty() when chat not found or has no title)
    backend2 = InMemoryBackend()
    _apply_settings(backend2, profile_enabled=False)
    settings2 = AppSettings(backend=backend2)
    settings2.load()
    svc._infra._settings = settings2
    # Use non-existent chat_id so build_chat_context returns ChatRequestContext with chat_title=None
    chat_id2 = 999999
    result2 = svc.get_context_explanation(chat_id2, None, None, return_trace=True)
    assert result2 is not None
    assert result2.explanation is not None, "empty context path must attach explanation"
    assert result2.explanation.empty_result is True
    assert result2.explanation.empty_result_reason == "no_sources"

    # Path 3: all fields excluded (fragment empty)
    backend3 = InMemoryBackend()
    backend3.setValue("chat_context_mode", "semantic")
    backend3.setValue("chat_context_detail_level", "standard")
    backend3.setValue("chat_context_profile_enabled", False)
    backend3.setValue("chat_context_include_project", False)
    backend3.setValue("chat_context_include_chat", False)
    backend3.setValue("chat_context_include_topic", False)
    settings3 = AppSettings(backend=backend3)
    settings3.load()
    svc._infra._settings = settings3
    proj_id3 = get_project_service().create_project("P3", "", "active")
    topic_id3 = get_topic_service().create_topic(proj_id3, "T3", "")
    chat_id3 = svc.create_chat_in_project(proj_id3, "C3", topic_id=topic_id3)
    result3 = svc.get_context_explanation(chat_id3, None, None, return_trace=True)
    assert result3 is not None
    assert result3.explanation is not None, "empty fragment path must attach explanation"
    assert result3.explanation.empty_result is True

    # Path 4: normal return (fragment present)
    backend4 = InMemoryBackend()
    _apply_settings(backend4, profile_enabled=False)
    settings4 = AppSettings(backend=backend4)
    settings4.load()
    svc._infra._settings = settings4
    proj_id4 = get_project_service().create_project("ExplainProj", "", "active")
    topic_id4 = get_topic_service().create_topic(proj_id4, "ExplainTopic", "")
    chat_id4 = svc.create_chat_in_project(proj_id4, "ExplainChat", topic_id=topic_id4)
    result4 = svc.get_context_explanation(chat_id4, None, None, return_trace=True)
    assert result4 is not None
    assert result4.explanation is not None, "normal path must attach explanation"
    assert result4.explanation.empty_result is False
    assert len(result4.explanation.sources) > 0


def test_formatted_explanation_snapshot(services):
    """Formatierte Explanation-Ausgabe entspricht Golden-Snapshot."""
    backend = InMemoryBackend()
    _apply_settings(backend, profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("ExplainProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "ExplainTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "ExplainChat", topic_id=topic_id
    )

    explanation = get_chat_service().get_context_explanation(chat_id, None, None)
    formatted = format_context_explanation(expl=explanation)

    golden_path = Path(__file__).resolve().parent / "expected" / "formatted_explanation.txt"
    assert_snapshot(formatted, golden_path, label="formatted", create_if_missing=False)
