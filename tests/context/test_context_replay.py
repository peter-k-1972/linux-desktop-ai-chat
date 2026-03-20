"""
Tests for Context Decision Replay System.

No DB access in replay. No randomness. No time dependency.
Identical input must produce identical output.

STRICT: DeepDiff must return empty. No ignore_order=True.
FAIL: Any difference = FAIL. Signature mismatch = FAIL.
"""

import pytest

from app.context.replay.replay_builder import from_live_request
from app.context.replay.replay_diff import (
    assert_replay_qa_pass,
    are_identical,
    classify_drift,
    diff_replay_output,
)
from app.context.replay.replay_models import CURRENT_VERSION, ReplayInput, ReplayVersionMismatchError
from app.context.replay.replay_service import compute_replay_signature, get_context_replay_service
from tests.helpers.repro_failure_helper import record_repro_case_on_failure


def _context_to_dict(context: object) -> dict:
    """Serialize ChatRequestContext to dict for comparison."""
    if context is None:
        return {}
    return {
        "project_id": getattr(context, "project_id", None),
        "project_name": getattr(context, "project_name", None),
        "chat_id": getattr(context, "chat_id", None),
        "chat_title": getattr(context, "chat_title", None),
        "topic_id": getattr(context, "topic_id", None),
        "topic_name": getattr(context, "topic_name", None),
        "is_global_chat": getattr(context, "is_global_chat", False),
    }




@pytest.fixture
def minimal_replay_input() -> ReplayInput:
    """Minimal ReplayInput for testing."""
    return ReplayInput(
        chat_id=1,
        project_id=1,
        project_name="Test Project",
        chat_title="Test Chat",
        topic_id=None,
        topic_name=None,
        is_global_chat=False,
        mode="semantic",
        detail="standard",
        include_project=True,
        include_chat=True,
        include_topic=False,
        max_project_chars=80,
        max_chat_chars=80,
        max_topic_chars=60,
        max_total_lines=6,
        limits_source="default",
        source="individual_settings",
        profile=None,
        policy=None,
        hint=None,
        chat_policy=None,
        project_policy=None,
        profile_enabled=False,
        fields=(),
        system_version=CURRENT_VERSION,
    )


def test_replay_produces_output(minimal_replay_input: ReplayInput) -> None:
    """Replay must produce fragment, explanation, and signature."""
    svc = get_context_replay_service()
    result = svc.replay(minimal_replay_input)
    assert result.fragment is not None
    assert result.explanation is not None
    assert "Arbeitskontext:" in (result.fragment or "")
    d = result.to_dict()
    assert "signature" in d
    assert isinstance(d["signature"], str)
    assert len(d["signature"]) == 64  # sha256 hex


def test_replay_deterministic(minimal_replay_input: ReplayInput, tmp_path) -> None:
    """Identical input must produce identical output. Signature equality required."""
    svc = get_context_replay_service()
    r1 = svc.replay(minimal_replay_input)
    r2 = svc.replay(minimal_replay_input)
    d1 = r1.to_dict()
    d2 = r2.to_dict()
    record_repro_case_on_failure(
        minimal_replay_input,
        d1,
        d2,
        tmp_path / "repro_failures",
        msg="Replay vs replay",
    )


def test_replay_vs_replay_identical(minimal_replay_input: ReplayInput, tmp_path) -> None:
    """
    Two replay runs with identical input must produce identical output.
    ASSERT: diff empty, signature equality. FAIL: any diff != {}, signature mismatch.
    """
    svc = get_context_replay_service()
    r1 = svc.replay(minimal_replay_input)
    r2 = svc.replay(minimal_replay_input)
    d1 = r1.to_dict()
    d2 = r2.to_dict()

    record_repro_case_on_failure(
        minimal_replay_input,
        d1,
        d2,
        tmp_path / "repro_failures",
        msg="Replay vs replay",
    )

    assert d1["context"] == d2["context"], "context must be identical"
    assert d1["trace"] == d2["trace"], "trace must be identical"
    assert d1["explanation"] == d2["explanation"], "explanation must be identical"
    assert d1["signature"] == d2["signature"], "signature must match"


def test_classify_drift() -> None:
    """Diff classifier returns CONTEXT_DRIFT, TRACE_DRIFT, EXPLAINABILITY_DRIFT."""
    from app.context.replay.replay_diff import DriftType
    from deepdiff import DeepDiff

    a = {"fragment": "x", "context": {}, "trace": {}, "explanation": {}}
    b = {"fragment": "y", "context": {}, "trace": {}, "explanation": {}}
    diff = DeepDiff(a, b)
    drifts = classify_drift(diff)
    assert DriftType.CONTEXT_DRIFT in drifts

    a = {"fragment": "x", "context": {}, "trace": {"x": 1}, "explanation": {}}
    b = {"fragment": "x", "context": {}, "trace": {"x": 2}, "explanation": {}}
    diff = DeepDiff(a, b)
    drifts = classify_drift(diff)
    assert DriftType.TRACE_DRIFT in drifts

    a = {"fragment": "x", "context": {}, "trace": {}, "explanation": {"a": 1}}
    b = {"fragment": "x", "context": {}, "trace": {}, "explanation": {"a": 2}}
    diff = DeepDiff(a, b)
    drifts = classify_drift(diff)
    assert DriftType.EXPLAINABILITY_DRIFT in drifts


def test_assert_replay_qa_pass_fails_on_diff() -> None:
    """assert_replay_qa_pass raises on any diff."""
    a = {"fragment": "x", "context": {}, "trace": {}, "explanation": {}, "signature": "abc"}
    b = {"fragment": "y", "context": {}, "trace": {}, "explanation": {}, "signature": "abc"}
    with pytest.raises(AssertionError, match="FAIL: diff not empty"):
        assert_replay_qa_pass(a, b)


def test_assert_replay_qa_pass_fails_on_signature_mismatch() -> None:
    """assert_replay_qa_pass raises on signature mismatch."""
    d = {"fragment": "x", "context": {}, "trace": {}, "explanation": {}}
    d["signature"] = compute_replay_signature(d)
    a = dict(d)
    b = dict(d)
    b["signature"] = "wrong"
    with pytest.raises(AssertionError, match="FAIL: signature mismatch"):
        assert_replay_qa_pass(a, b)


def test_version_mismatch_raises(minimal_replay_input: ReplayInput) -> None:
    """Replay with system_version mismatch raises ReplayVersionMismatchError."""
    from dataclasses import replace

    wrong_version = replace(minimal_replay_input, system_version="0.9")
    svc = get_context_replay_service()
    with pytest.raises(ReplayVersionMismatchError, match="version mismatch"):
        svc.replay(wrong_version)


def test_allow_version_mismatch_bypasses(minimal_replay_input: ReplayInput) -> None:
    """Replay with allow_version_mismatch=True skips version check."""
    from dataclasses import replace

    wrong_version = replace(minimal_replay_input, system_version="0.9")
    svc = get_context_replay_service()
    result = svc.replay(wrong_version, allow_version_mismatch=True)
    assert result.fragment is not None


def test_replay_missing_version_raises() -> None:
    """ReplayInput with system_version=None raises on replay."""
    inp = ReplayInput(
        chat_id=1,
        project_id=1,
        project_name="Test",
        chat_title="Chat",
        topic_id=None,
        topic_name=None,
        is_global_chat=False,
        mode="semantic",
        detail="standard",
        include_project=True,
        include_chat=True,
        include_topic=False,
        max_project_chars=80,
        max_chat_chars=80,
        max_topic_chars=60,
        max_total_lines=6,
        limits_source="default",
        source="individual_settings",
        profile=None,
        policy=None,
        hint=None,
        chat_policy=None,
        project_policy=None,
        profile_enabled=False,
        fields=(),
        system_version=None,
    )
    svc = get_context_replay_service()
    with pytest.raises(ReplayVersionMismatchError, match="version mismatch"):
        svc.replay(inp)


def test_diff_ignore_order_false() -> None:
    """DeepDiff must use ignore_order=False (list order matters)."""
    a = {"items": [1, 2, 3]}
    b = {"items": [1, 3, 2]}
    diff = diff_replay_output(a, b, ignore_order=False)
    assert not are_identical(a, b)
    assert are_identical(a, a)


@pytest.fixture
def replay_live_services():
    """DB and services for live vs replay test."""
    import os
    import tempfile

    from PySide6.QtWidgets import QApplication
    from app.core.config.settings import AppSettings
    from app.core.config.settings_backend import InMemoryBackend
    from app.core.db.database_manager import DatabaseManager
    from app.services.chat_service import ChatService, get_chat_service, set_chat_service
    from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
    from app.services.project_service import ProjectService, get_project_service, set_project_service
    from app.services.topic_service import TopicService, get_topic_service, set_topic_service

    app = QApplication.instance()
    if not app:
        app = QApplication([])

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseManager(db_path=path)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = None
    set_infrastructure(infra)
    set_project_service(ProjectService())
    set_chat_service(ChatService())
    set_topic_service(TopicService())

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

    proj_id = get_project_service().create_project("ReplayProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "ReplayTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "ReplayChat", topic_id=topic_id
    )

    try:
        yield chat_id
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
        set_project_service(None)
        set_chat_service(None)
        set_topic_service(None)
        set_infrastructure(None)


def test_live_vs_replay(replay_live_services: int, tmp_path) -> None:
    """
    Live run output must match replay run output.
    Capture from live, replay, compare. ASSERT: diff empty, signature equality.
    FAIL: any diff != {}, signature mismatch.
    """
    from app.context.explainability.context_explanation_serializer import (
        explanation_to_dict,
        trace_to_dict,
    )
    from app.context.replay.canonicalize import canonicalize
    from app.services.chat_service import get_chat_service

    chat_id = replay_live_services
    chat_svc = get_chat_service()
    result = chat_svc.get_context_explanation(
        chat_id,
        return_trace=True,
        return_fragment=True,
    )
    trace, fragment, context, render_options = result

    replay_input = from_live_request(trace, context, render_options)
    replay_svc = get_context_replay_service()
    replay_result = replay_svc.replay(replay_input)

    live_dict = {
        "fragment": fragment,
        "context": _context_to_dict(context),
        "trace": trace_to_dict(
            trace,
            include_explanation=False,
            include_budget=True,
            include_dropped=True,
        ),
        "explanation": explanation_to_dict(
            trace.explanation or trace,
            include_budget=True,
            include_dropped=True,
        ),
    }
    live_dict = canonicalize(live_dict)
    live_dict["signature"] = compute_replay_signature(live_dict)
    replay_dict = replay_result.to_dict()

    record_repro_case_on_failure(
        replay_input,
        live_dict,
        replay_dict,
        tmp_path / "repro_failures",
        msg="Live vs replay",
    )

    assert live_dict["context"] == replay_dict["context"], "context must be identical"
    assert live_dict["trace"] == replay_dict["trace"], "trace must be identical"
    assert live_dict["explanation"] == replay_dict["explanation"], "explanation must be identical"
    assert live_dict["signature"] == replay_dict["signature"], "signature must match"


def test_deterministic_forbids_random() -> None:
    """Deterministic context must forbid random."""
    import random

    from app.context.engine import DeterminismViolation, _deterministic_context

    with _deterministic_context():
        with pytest.raises(DeterminismViolation, match="random forbidden"):
            random.random()


def test_sorted_dict_items_deterministic() -> None:
    """_sorted_dict_items yields in sorted key order."""
    from app.context.engine import _sorted_dict_items

    d = {"z": 1, "a": 2, "m": 3}
    items = list(_sorted_dict_items(d))
    assert items == [("a", 2), ("m", 3), ("z", 1)]


def test_from_live_request() -> None:
    """from_live_request builds ReplayInput from trace, context, render_options."""
    from app.chat.context import ChatContextRenderOptions, ChatRequestContext
    from app.chat.context_profiles import ChatContextResolutionTrace

    trace = ChatContextResolutionTrace(
        source="policy",
        profile="balanced",
        mode="semantic",
        detail="standard",
        fields=["project", "chat"],
        policy="architecture",
        hint=None,
        chat_policy=None,
        project_policy=None,
        profile_enabled=False,
        limits_source="policy",
        max_project_chars=80,
        max_chat_chars=80,
        max_topic_chars=60,
        max_total_lines=6,
        explanation=None,
    )
    context = ChatRequestContext(
        project_id=1,
        project_name="Proj",
        chat_id=1,
        chat_title="Chat",
        topic_id=None,
        topic_name=None,
        is_global_chat=False,
    )
    render_options = ChatContextRenderOptions(
        include_project=True,
        include_chat=True,
        include_topic=False,
    )
    inp = from_live_request(trace, context, render_options)
    assert inp.chat_id == 1
    assert inp.project_name == "Proj"
    assert inp.mode == "semantic"
    assert inp.source == "policy"
