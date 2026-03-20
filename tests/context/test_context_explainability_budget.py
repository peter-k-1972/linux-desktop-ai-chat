"""
QA coverage for context budget explainability.

Uses real resolver, no fake explanation objects.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_limits import CHARS_PER_TOKEN
from app.chat.context_policies import ChatContextPolicy
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


def _apply_settings(backend: InMemoryBackend, *, profile_enabled: bool = False):
    backend.setValue("chat_context_mode", "semantic")
    backend.setValue("chat_context_detail_level", "standard")
    backend.setValue("chat_context_profile_enabled", profile_enabled)
    backend.setValue("chat_context_include_project", True)
    backend.setValue("chat_context_include_chat", True)
    backend.setValue("chat_context_include_topic", True)


def _setup_chat(services) -> int:
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
    return chat_id


def test_budget_fields_populated(services):
    """Budget fields are populated when explanation is returned."""
    chat_id = _setup_chat(services)
    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    assert explanation.configured_budget_total is not None
    assert explanation.effective_budget_total is not None
    assert explanation.reserved_budget_system is not None
    assert explanation.reserved_budget_user is not None
    assert explanation.available_budget_for_context is not None
    assert explanation.budget_strategy is not None
    assert explanation.budget_source is not None


def test_available_budget_consistent_with_reservations(services):
    """available_budget_for_context equals effective minus reserved."""
    chat_id = _setup_chat(services)
    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    if (
        explanation.effective_budget_total is not None
        and explanation.reserved_budget_system is not None
        and explanation.reserved_budget_user is not None
    ):
        expected = (
            explanation.effective_budget_total
            - explanation.reserved_budget_system
            - explanation.reserved_budget_user
        )
        if expected < 0:
            expected = 0
        assert explanation.available_budget_for_context == expected


def test_per_source_budget_accounting_sums(services):
    """Per-source budget_used + budget_dropped equals chars_before (in chars)."""
    chat_id = _setup_chat(services)
    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    for src in explanation.sources:
        used = src.budget_used or 0
        dropped = src.budget_dropped or 0
        chars_before = src.chars_before or 0
        assert used + dropped == chars_before


def test_dropped_total_equals_sum_of_dropped_entries(services):
    """dropped_total_tokens equals sum of dropped_by_source dropped_tokens."""
    backend = InMemoryBackend()
    _apply_settings(backend, profile_enabled=True)
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

    if explanation.dropped_by_source:
        summed = sum(
            e.dropped_tokens or 0 for e in explanation.dropped_by_source
        )
        assert explanation.dropped_total_tokens == summed


def test_skipped_sources_budget_exhaustion_visible(services):
    """Skipped sources due to budget exhaustion are visible in explanation."""
    from app.chat.context_limits import ChatContextRenderLimits

    def _limits_max_lines_3(policy):
        return ChatContextRenderLimits(
            max_project_chars=100,
            max_chat_chars=100,
            max_topic_chars=80,
            max_total_lines=3,
        )

    chat_id = _setup_chat(services)

    with patch(
        "app.chat.context_policies.resolve_limits_for_policy",
        side_effect=_limits_max_lines_3,
    ):
        explanation = get_chat_service().get_context_explanation(
            chat_id, None, ChatContextPolicy.ARCHITECTURE
        )

    exhausted = [
        s for s in explanation.sources
        if s.reason == "budget_exhausted"
    ]
    assert len(exhausted) >= 1
    topic_src = next(
        (s for s in explanation.sources if s.source_type == "topic"), None
    )
    assert topic_src is not None
    assert topic_src.included is False
    assert topic_src.reason == "budget_exhausted"


def test_source_ordering_matches_resolver_order(services):
    """Source selection_order in explanation matches resolver order (1=project, 2=chat, 3=topic)."""
    chat_id = _setup_chat(services)
    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    by_order = sorted(
        explanation.sources,
        key=lambda s: s.selection_order or 999,
    )
    types = [s.source_type for s in by_order]
    assert types == ["project", "chat", "topic"]


def test_formatted_debug_output_deterministic(services):
    """Formatted debug output is deterministic (same input -> same output)."""
    chat_id = _setup_chat(services)
    explanation = get_chat_service().get_context_explanation(chat_id, None, None)

    out1 = format_context_explanation(expl=explanation)
    out2 = format_context_explanation(expl=explanation)
    assert out1 == out2, (
        "format_context_explanation non-deterministic: two calls on same explanation produced different output. "
        "Check for dict/set iteration, random values, or timestamp injection in formatter."
    )


# --- Snapshot tests ---

def _snapshot_path(name: str) -> Path:
    return Path(__file__).resolve().parent / "expected" / f"budget_{name}.txt"


def test_snapshot_normal_request(services):
    """Snapshot: normal request, all sources included."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, None, return_trace=True
    )
    formatted = format_context_explanation(expl=trace.explanation, trace=trace)

    golden = _snapshot_path("normal_request")
    assert_snapshot(formatted, golden, label="formatted")


def test_snapshot_compressed_request(services):
    """Snapshot: compressed request (long project name truncated)."""
    backend = InMemoryBackend()
    _apply_settings(backend, profile_enabled=False)
    settings = AppSettings(backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project(
        "A" * 100,
        "",
        "active",
    )
    topic_id = get_topic_service().create_topic(proj_id, "Topic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "Chat", topic_id=topic_id
    )

    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    formatted = format_context_explanation(expl=trace.explanation, trace=trace)

    golden = _snapshot_path("compressed_request")
    assert_snapshot(formatted, golden, label="formatted")


def test_snapshot_budget_exhausted_request(services):
    """Snapshot: budget exhausted (line limit cuts topic)."""
    from app.chat.context_limits import ChatContextRenderLimits

    def _limits_max_lines_3(policy):
        return ChatContextRenderLimits(
            max_project_chars=100,
            max_chat_chars=100,
            max_topic_chars=80,
            max_total_lines=3,
        )

    chat_id = _setup_chat(services)

    with patch(
        "app.chat.context_policies.resolve_limits_for_policy",
        side_effect=_limits_max_lines_3,
    ):
        trace = get_chat_service().get_context_explanation(
            chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
        )

    formatted = format_context_explanation(expl=trace.explanation, trace=trace)

    golden = _snapshot_path("budget_exhausted_request")
    assert_snapshot(formatted, golden, label="formatted")
