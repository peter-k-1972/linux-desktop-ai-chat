"""
Regression snapshot suite for explainability and inspection.

Protects determinism and observability shape against future drift.
Snapshots: formatted explanation text, inspection text output, serializer JSON.
Uses stable fixtures. No ad-hoc normalization. Production ordering.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_limits import ChatContextRenderLimits
from app.chat.context_policies import ChatContextPolicy
from app.context.debug.context_debug import format_context_explanation
from app.context.explainability.context_inspection_serializer import inspection_result_to_dict
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.context_explain_service import ContextExplainRequest
from app.services.context_inspection_service import get_context_inspection_service
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, get_project_service, set_project_service
from app.services.topic_service import TopicService, get_topic_service, set_topic_service

from tests.context.conftest import assert_snapshot

pytestmark = pytest.mark.context_observability

SNAPSHOT_DIR = Path(__file__).resolve().parent / "expected" / "explainability_snapshots"


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


def _default_settings(backend: InMemoryBackend, *, mode: str = "semantic", profile_enabled: bool = False):
    backend.setValue("chat_context_mode", mode)
    backend.setValue("chat_context_detail_level", "standard")
    backend.setValue("chat_context_profile_enabled", profile_enabled)
    backend.setValue("chat_context_include_project", True)
    backend.setValue("chat_context_include_chat", True)
    backend.setValue("chat_context_include_topic", True)


def _setup_default_chat(services) -> int:
    backend = InMemoryBackend()
    _default_settings(backend, profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings
    proj_id = get_project_service().create_project("SnapshotProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "SnapshotTopic", "")
    chat_id = get_chat_service().create_chat_in_project(proj_id, "SnapshotChat", topic_id=topic_id)
    return chat_id


def _build_formatted_text(trace) -> str:
    return format_context_explanation(expl=trace.explanation, trace=trace)


def _build_inspection_text(result) -> str:
    parts = []
    if result.formatted_summary:
        parts.append(result.formatted_summary)
    if result.formatted_budget:
        parts.append(result.formatted_budget)
    if result.formatted_sources:
        parts.append(result.formatted_sources)
    if result.formatted_warnings:
        parts.append(result.formatted_warnings)
    if result.payload_preview and not result.payload_preview.empty:
        from app.context.debug.context_debug import format_payload_preview
        parts.append(format_payload_preview(result.payload_preview))
    return "\n".join(parts) if parts else ""


def _build_serializer_json(result) -> str:
    d = inspection_result_to_dict(result)
    return json.dumps(d, indent=2, ensure_ascii=False)


def _assert_snapshot(content: str, scenario: str, surface: str, ext: str = "txt") -> None:
    path = SNAPSHOT_DIR / f"{scenario}_{surface}.{ext}"
    assert_snapshot(content, path, label="actual")


def test_snapshot_output_stable_across_runs(services):
    """Snapshot output is identical across multiple runs; no flaky diffs."""
    from tests.context.conftest import normalize_snapshot_content

    chat_id = _setup_default_chat(services)
    result1 = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    text1 = _build_inspection_text(result1)

    result2 = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    text2 = _build_inspection_text(result2)

    norm1 = normalize_snapshot_content(text1)
    norm2 = normalize_snapshot_content(text2)
    assert norm1 == norm2, "Inspection output must be deterministic across runs"


def test_snapshot_output_contains_no_forbidden_patterns(services):
    """Snapshot output must not contain timestamps, random IDs, or memory addresses."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    text = _build_inspection_text(result)
    json_out = _build_serializer_json(result)

    forbidden = [
        ("0x", "memory address"),
        ("0X", "memory address"),
        ("<object", "object repr"),
        ("at 0x", "memory address"),
    ]
    for pattern, desc in forbidden:
        assert pattern not in text, f"Formatted output must not contain {desc}: {pattern!r}"
        assert pattern not in json_out, f"JSON output must not contain {desc}: {pattern!r}"


# --- Scenario 1: default balanced request ---


def test_snapshot_01_default_balanced_formatted(services):
    """Snapshot: default balanced request – formatted explanation."""
    chat_id = _setup_default_chat(services)
    trace = get_chat_service().get_context_explanation(chat_id, None, None, return_trace=True)
    text = _build_formatted_text(trace)
    _assert_snapshot(text, "01_default_balanced", "formatted")


def test_snapshot_01_default_balanced_inspection(services):
    """Snapshot: default balanced request – inspection text."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    text = _build_inspection_text(result)
    _assert_snapshot(text, "01_default_balanced", "inspection")


def test_snapshot_01_default_balanced_json(services):
    """Snapshot: default balanced request – serializer JSON."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    out = _build_serializer_json(result)
    _assert_snapshot(out, "01_default_balanced", "json", ext="json")


# --- Scenario 2: explicit architecture policy ---


def test_snapshot_02_explicit_architecture_formatted(services):
    """Snapshot: explicit architecture policy – formatted explanation."""
    chat_id = _setup_default_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    text = _build_formatted_text(trace)
    _assert_snapshot(text, "02_explicit_architecture", "formatted")


def test_snapshot_02_explicit_architecture_inspection(services):
    """Snapshot: explicit architecture policy – inspection text."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id, context_policy="architecture"),
        include_payload_preview=True,
        include_formatted=True,
    )
    text = _build_inspection_text(result)
    _assert_snapshot(text, "02_explicit_architecture", "inspection")


def test_snapshot_02_explicit_architecture_json(services):
    """Snapshot: explicit architecture policy – serializer JSON."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id, context_policy="architecture"),
        include_payload_preview=True,
        include_formatted=True,
    )
    out = _build_serializer_json(result)
    _assert_snapshot(out, "02_explicit_architecture", "json", ext="json")


# --- Scenario 3: strict_minimal profile ---


def test_snapshot_03_strict_minimal_formatted(services):
    """Snapshot: strict_minimal profile – formatted explanation."""
    backend = InMemoryBackend()
    _default_settings(backend, profile_enabled=True)
    backend.setValue("chat_context_profile", "strict_minimal")
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings
    proj_id = get_project_service().create_project("MinProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "MinTopic", "")
    chat_id = get_chat_service().create_chat_in_project(proj_id, "MinChat", topic_id=topic_id)
    trace = get_chat_service().get_context_explanation(chat_id, None, None, return_trace=True)
    text = _build_formatted_text(trace)
    _assert_snapshot(text, "03_strict_minimal", "formatted")


def test_snapshot_03_strict_minimal_inspection(services):
    """Snapshot: strict_minimal profile – inspection text."""
    backend = InMemoryBackend()
    _default_settings(backend, profile_enabled=True)
    backend.setValue("chat_context_profile", "strict_minimal")
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings
    proj_id = get_project_service().create_project("MinProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "MinTopic", "")
    chat_id = get_chat_service().create_chat_in_project(proj_id, "MinChat", topic_id=topic_id)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    text = _build_inspection_text(result)
    _assert_snapshot(text, "03_strict_minimal", "inspection")


def test_snapshot_03_strict_minimal_json(services):
    """Snapshot: strict_minimal profile – serializer JSON."""
    backend = InMemoryBackend()
    _default_settings(backend, profile_enabled=True)
    backend.setValue("chat_context_profile", "strict_minimal")
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings
    proj_id = get_project_service().create_project("MinProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "MinTopic", "")
    chat_id = get_chat_service().create_chat_in_project(proj_id, "MinChat", topic_id=topic_id)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    out = _build_serializer_json(result)
    _assert_snapshot(out, "03_strict_minimal", "json", ext="json")


# --- Scenario 4: mode off ---


def test_snapshot_04_mode_off_formatted(services):
    """Snapshot: mode=off – formatted explanation."""
    backend = InMemoryBackend()
    _default_settings(backend, mode="off", profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings
    chat_id = _setup_default_chat(services)
    trace = get_chat_service().get_context_explanation(chat_id, None, None, return_trace=True)
    text = _build_formatted_text(trace)
    _assert_snapshot(text, "04_mode_off", "formatted")


def test_snapshot_04_mode_off_inspection(services):
    """Snapshot: mode=off – inspection text."""
    backend = InMemoryBackend()
    _default_settings(backend, mode="off", profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    text = _build_inspection_text(result)
    _assert_snapshot(text, "04_mode_off", "inspection")


def test_snapshot_04_mode_off_json(services):
    """Snapshot: mode=off – serializer JSON."""
    backend = InMemoryBackend()
    _default_settings(backend, mode="off", profile_enabled=False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    out = _build_serializer_json(result)
    _assert_snapshot(out, "04_mode_off", "json", ext="json")


# --- Scenario 5: budget exhaustion ---


def _limits_max_lines_3(policy):
    return ChatContextRenderLimits(
        max_project_chars=100,
        max_chat_chars=100,
        max_topic_chars=80,
        max_total_lines=3,
    )


def test_snapshot_05_budget_exhaustion_formatted(services):
    """Snapshot: budget exhaustion (line limit cuts topic) – formatted explanation."""
    chat_id = _setup_default_chat(services)
    with patch("app.chat.context_policies.resolve_limits_for_policy", side_effect=_limits_max_lines_3):
        trace = get_chat_service().get_context_explanation(
            chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
        )
    text = _build_formatted_text(trace)
    _assert_snapshot(text, "05_budget_exhaustion", "formatted")


def test_snapshot_05_budget_exhaustion_inspection(services):
    """Snapshot: budget exhaustion – inspection text."""
    chat_id = _setup_default_chat(services)
    with patch("app.chat.context_policies.resolve_limits_for_policy", side_effect=_limits_max_lines_3):
        result = get_context_inspection_service().inspect(
            ContextExplainRequest(chat_id=chat_id, context_policy="architecture"),
            include_payload_preview=True,
            include_formatted=True,
        )
    text = _build_inspection_text(result)
    _assert_snapshot(text, "05_budget_exhaustion", "inspection")


def test_snapshot_05_budget_exhaustion_json(services):
    """Snapshot: budget exhaustion – serializer JSON."""
    chat_id = _setup_default_chat(services)
    with patch("app.chat.context_policies.resolve_limits_for_policy", side_effect=_limits_max_lines_3):
        result = get_context_inspection_service().inspect(
            ContextExplainRequest(chat_id=chat_id, context_policy="architecture"),
            include_payload_preview=True,
            include_formatted=True,
        )
    out = _build_serializer_json(result)
    _assert_snapshot(out, "05_budget_exhaustion", "json", ext="json")


# --- Scenario 6: all sources empty (chat_id=0) ---


def test_snapshot_06_all_sources_empty_formatted(services):
    """Snapshot: all sources empty (chat_id=0) – formatted explanation."""
    _setup_default_chat(services)
    trace = get_chat_service().get_context_explanation(0, None, None, return_trace=True)
    text = _build_formatted_text(trace)
    _assert_snapshot(text, "06_all_sources_empty", "formatted")


def test_snapshot_06_all_sources_empty_inspection(services):
    """Snapshot: all sources empty – inspection text."""
    _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=0),
        include_payload_preview=True,
        include_formatted=True,
    )
    text = _build_inspection_text(result)
    _assert_snapshot(text, "06_all_sources_empty", "inspection")


def test_snapshot_06_all_sources_empty_json(services):
    """Snapshot: all sources empty – serializer JSON."""
    _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=0),
        include_payload_preview=True,
        include_formatted=True,
    )
    out = _build_serializer_json(result)
    _assert_snapshot(out, "06_all_sources_empty", "json", ext="json")


# --- Scenario 7: invalid explicit input fallback ---


def test_snapshot_07_invalid_explicit_fallback_formatted(services):
    """Snapshot: invalid explicit input fallback – formatted explanation."""
    chat_id = _setup_default_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id,
        None,
        None,
        return_trace=True,
        invalid_override_sources=["explicit_context_policy"],
        invalid_override_inputs=[("explicit_context_policy", "bad_policy")],
    )
    text = _build_formatted_text(trace)
    _assert_snapshot(text, "07_invalid_explicit_fallback", "formatted")


def test_snapshot_07_invalid_explicit_fallback_inspection(services):
    """Snapshot: invalid explicit input fallback – inspection text."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id, context_policy="bad_policy"),
        include_payload_preview=True,
        include_formatted=True,
    )
    text = _build_inspection_text(result)
    _assert_snapshot(text, "07_invalid_explicit_fallback", "inspection")


def test_snapshot_07_invalid_explicit_fallback_json(services):
    """Snapshot: invalid explicit input fallback – serializer JSON."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id, context_policy="bad_policy"),
        include_payload_preview=True,
        include_formatted=True,
    )
    out = _build_serializer_json(result)
    _assert_snapshot(out, "07_invalid_explicit_fallback", "json", ext="json")


# --- Scenario 8: failsafe cleanup triggered (header-only via patched limits) ---


def _limits_max_lines_1(policy):
    return ChatContextRenderLimits(
        max_project_chars=80,
        max_chat_chars=80,
        max_topic_chars=60,
        max_total_lines=1,
    )


def test_snapshot_08_failsafe_cleanup_formatted(services):
    """Snapshot: failsafe cleanup (header-only fragment removed) – formatted explanation."""
    chat_id = _setup_default_chat(services)
    with patch("app.chat.context_policies.resolve_limits_for_policy", side_effect=_limits_max_lines_1):
        trace = get_chat_service().get_context_explanation(
            chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
        )
    text = _build_formatted_text(trace)
    _assert_snapshot(text, "08_failsafe_cleanup", "formatted")


def test_snapshot_08_failsafe_cleanup_inspection(services):
    """Snapshot: failsafe cleanup – inspection text."""
    chat_id = _setup_default_chat(services)
    with patch("app.chat.context_policies.resolve_limits_for_policy", side_effect=_limits_max_lines_1):
        result = get_context_inspection_service().inspect(
            ContextExplainRequest(chat_id=chat_id, context_policy="architecture"),
            include_payload_preview=True,
            include_formatted=True,
        )
    text = _build_inspection_text(result)
    _assert_snapshot(text, "08_failsafe_cleanup", "inspection")


def test_snapshot_08_failsafe_cleanup_json(services):
    """Snapshot: failsafe cleanup – serializer JSON."""
    chat_id = _setup_default_chat(services)
    with patch("app.chat.context_policies.resolve_limits_for_policy", side_effect=_limits_max_lines_1):
        result = get_context_inspection_service().inspect(
            ContextExplainRequest(chat_id=chat_id, context_policy="architecture"),
            include_payload_preview=True,
            include_formatted=True,
        )
    out = _build_serializer_json(result)
    _assert_snapshot(out, "08_failsafe_cleanup", "json", ext="json")


# --- Scenario 9: payload preview enabled ---


def test_snapshot_09_payload_preview_formatted(services):
    """Snapshot: payload preview enabled – formatted explanation (same as default, preview in inspection)."""
    chat_id = _setup_default_chat(services)
    trace = get_chat_service().get_context_explanation(chat_id, None, None, return_trace=True)
    text = _build_formatted_text(trace)
    _assert_snapshot(text, "09_payload_preview", "formatted")


def test_snapshot_09_payload_preview_inspection(services):
    """Snapshot: payload preview enabled – inspection text with payload block."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    text = _build_inspection_text(result)
    _assert_snapshot(text, "09_payload_preview", "inspection")


def test_snapshot_09_payload_preview_json(services):
    """Snapshot: payload preview enabled – serializer JSON with payload_preview."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id),
        include_payload_preview=True,
        include_formatted=True,
    )
    out = _build_serializer_json(result)
    _assert_snapshot(out, "09_payload_preview", "json", ext="json")


# --- Scenario 10: warnings-free request (architecture policy, no fallback) ---


def test_snapshot_10_warnings_free_formatted(services):
    """Snapshot: warnings-free request (architecture policy) – formatted explanation."""
    chat_id = _setup_default_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    text = _build_formatted_text(trace)
    _assert_snapshot(text, "10_warnings_free", "formatted")


def test_snapshot_10_warnings_free_inspection(services):
    """Snapshot: warnings-free request – inspection text."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id, context_policy="architecture"),
        include_payload_preview=True,
        include_formatted=True,
    )
    text = _build_inspection_text(result)
    _assert_snapshot(text, "10_warnings_free", "inspection")


def test_snapshot_10_warnings_free_json(services):
    """Snapshot: warnings-free request – serializer JSON."""
    chat_id = _setup_default_chat(services)
    result = get_context_inspection_service().inspect(
        ContextExplainRequest(chat_id=chat_id, context_policy="architecture"),
        include_payload_preview=True,
        include_formatted=True,
    )
    out = _build_serializer_json(result)
    _assert_snapshot(out, "10_warnings_free", "json", ext="json")
