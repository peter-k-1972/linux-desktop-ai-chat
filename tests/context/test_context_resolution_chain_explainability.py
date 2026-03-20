"""
QA coverage for resolution-chain explainability and ignored inputs.

Uses real resolver paths. No fabricated explanation objects.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_policies import ChatContextPolicy
from app.chat.request_context_hints import RequestContextHint
from app.context.debug.context_debug import format_context_explanation
from app.context.explainability.context_explanation_serializer import explanation_to_dict
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
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
    backend.setValue("chat_context_profile", "balanced")
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


# --- Unit tests ---


def test_winning_source_visible_for_effective_policy(services):
    """Winning source is visible for effective policy in resolved_settings."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None
    assert expl.resolved_settings

    for entry in expl.resolved_settings:
        assert entry.winning_source == "explicit_context_policy"
        assert entry.fallback_used is False


def test_candidate_list_preserves_exact_priority_order(services):
    """Candidate list preserves exact priority order (0..5)."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.DEBUG, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None

    expected_order = [
        "profile_enabled",
        "explicit_context_policy",
        "chat_default_context_policy",
        "project_default_context_policy",
        "request_context_hint",
        "individual_settings",
    ]
    for entry in expl.resolved_settings:
        assert len(entry.candidates) == 6
        for i, c in enumerate(entry.candidates):
            assert c.priority_index == i
            assert c.source == expected_order[i]


def test_skipped_candidates_include_skipped_reason(services):
    """Skipped candidates include skipped_reason (higher_priority_won or source_not_present)."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None

    for entry in expl.resolved_settings:
        applied = [c for c in entry.candidates if c.applied]
        skipped = [c for c in entry.candidates if not c.applied]
        assert len(applied) == 1
        for c in skipped:
            assert c.skipped_reason in ("higher_priority_won", "source_not_present")


def test_invalid_explicit_policy_visible_as_ignored_input(services):
    """Invalid explicit policy is visible as ignored input."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id,
        None,
        None,
        return_trace=True,
        invalid_override_sources=["explicit_context_policy"],
        invalid_override_inputs=[("explicit_context_policy", "invalid_policy_xyz")],
    )
    expl = trace.explanation
    assert expl is not None

    ignored = [i for i in expl.ignored_inputs if i.input_name == "explicit_context_policy"]
    assert len(ignored) == 1
    assert ignored[0].raw_value == "invalid_policy_xyz"
    assert ignored[0].reason == "invalid_value"
    assert ignored[0].resolution_effect == "ignored"


def test_missing_profile_visible_as_ignored_input(services):
    """Invalid request hint (missing profile) is visible as ignored input."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id,
        None,
        None,
        return_trace=True,
        invalid_override_sources=["request_context_hint"],
        invalid_override_inputs=[("request_context_hint", "unknown_hint_value")],
    )
    expl = trace.explanation
    assert expl is not None

    ignored = [i for i in expl.ignored_inputs if i.input_name == "request_context_hint"]
    assert len(ignored) == 1
    assert ignored[0].raw_value == "unknown_hint_value"
    assert ignored[0].reason == "invalid_value"
    assert ignored[0].resolution_effect == "ignored"


def test_fallback_used_marked_when_no_higher_priority_applied(services):
    """fallback_used is marked when individual_settings wins (no higher-priority source)."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, None, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None

    for entry in expl.resolved_settings:
        assert entry.winning_source == "individual_settings"
        assert entry.fallback_used is True


def test_json_serializer_output_deterministic(services):
    """JSON serializer output is deterministic (same input -> same output)."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None

    d1 = explanation_to_dict(expl)
    d2 = explanation_to_dict(expl)
    assert d1 == d2, (
        "explanation_to_dict non-deterministic: two calls on same input produced different dicts. "
        "Check for dict/set iteration order, random values, or timestamp injection."
    )

    json1 = json.dumps(d1, sort_keys=True)
    json2 = json.dumps(d2, sort_keys=True)
    assert json1 == json2, (
        "explanation_to_dict JSON output non-deterministic: same dict produced different JSON. "
        "Check key ordering or serialization of nested structures."
    )


def test_explanation_to_dict_ordering_contract(services):
    """explanation_to_dict uses fixed key order: resolved_settings, decisions, sources, ..."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, None, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None

    d = explanation_to_dict(expl)
    keys = list(d.keys())
    # Semantic order: resolved_settings, decisions, sources, compressions, warnings, ignored_inputs
    assert keys.index("resolved_settings") < keys.index("decisions")
    assert keys.index("decisions") < keys.index("sources")
    assert keys.index("sources") < keys.index("compressions")
    assert keys.index("compressions") < keys.index("warnings")
    assert keys.index("warnings") < keys.index("ignored_inputs")
    # sources ordered by selection_order (project, chat, topic)
    if d["sources"]:
        source_types = [s["source_type"] for s in d["sources"]]
        assert source_types == ["project", "chat", "topic"]


# --- Snapshot tests ---


def _snapshot_path(name: str) -> Path:
    return Path(__file__).resolve().parent / "expected" / f"resolution_chain_{name}.txt"


def test_snapshot_explicit_policy_wins(services):
    """Snapshot: explicit policy wins over hint and individual_settings."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id,
        RequestContextHint.LOW_CONTEXT_QUERY,
        ChatContextPolicy.ARCHITECTURE,
        return_trace=True,
    )
    formatted = format_context_explanation(expl=trace.explanation, trace=trace)

    golden = _snapshot_path("explicit_policy_wins")
    assert_snapshot(formatted, golden, label="formatted")


def test_snapshot_profile_wins(services):
    """Snapshot: profile wins when profile_enabled=True."""
    backend = InMemoryBackend()
    _apply_settings(backend, profile_enabled=True)
    backend.setValue("chat_context_profile", "full_guidance")
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("Proj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "Topic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "Chat", topic_id=topic_id
    )

    trace = get_chat_service().get_context_explanation(
        chat_id,
        RequestContextHint.LOW_CONTEXT_QUERY,
        ChatContextPolicy.ARCHITECTURE,
        return_trace=True,
    )
    formatted = format_context_explanation(expl=trace.explanation, trace=trace)

    golden = _snapshot_path("profile_wins")
    assert_snapshot(formatted, golden, label="formatted")


def test_snapshot_request_hint_fallback(services):
    """Snapshot: request hint fallback when no policy, no profile."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id,
        RequestContextHint.LOW_CONTEXT_QUERY,
        None,
        return_trace=True,
    )
    formatted = format_context_explanation(expl=trace.explanation, trace=trace)

    golden = _snapshot_path("request_hint_fallback")
    assert_snapshot(formatted, golden, label="formatted")


def test_snapshot_invalid_explicit_value_ignored(services):
    """Snapshot: invalid explicit policy value is ignored, fallback used."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id,
        None,
        None,
        return_trace=True,
        invalid_override_sources=["explicit_context_policy"],
        invalid_override_inputs=[("explicit_context_policy", "bad_policy")],
    )
    formatted = format_context_explanation(expl=trace.explanation, trace=trace)

    golden = _snapshot_path("invalid_explicit_value_ignored")
    assert_snapshot(formatted, golden, label="formatted")
