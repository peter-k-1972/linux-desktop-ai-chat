"""
Tests for Failure Replay Pipeline.

No DB access. No randomness. No datetime.
"""

import json
from pathlib import Path

import pytest

from app.context.replay.failure_recorder import load_repro_case, persist_repro_case
from app.context.replay.failure_types import CONTEXT_DRIFT, SIGNATURE_MISMATCH
from app.context.replay.repro_case_builder import build_repro_case, build_repro_case_from_failure
from app.context.replay.repro_case_models import FailureMetadata, ReproCase
from app.context.replay.repro_case_runner import (
    dict_to_replay_input,
    run_repro_case,
    run_repro_case_from_file,
    ReproRunResult,
)
from tests.helpers.repro_failure_helper import record_repro_case_on_failure


def test_build_repro_case() -> None:
    """Build ReproCase from explicit inputs."""
    replay_input = {"chat_id": 1, "mode": "semantic"}
    expected = {"fragment": "x", "signature": "abc"}
    meta = FailureMetadata(
        failure_type=CONTEXT_DRIFT,
        drift_types=(CONTEXT_DRIFT,),
        expected_signature="abc",
        actual_signature="def",
    )
    case = ReproCase(
        replay_input=replay_input,
        expected_result=expected,
        metadata=meta,
    )
    assert case.metadata.failure_type == CONTEXT_DRIFT


def test_build_repro_case_from_failure() -> None:
    """Build ReproCase from actual vs expected diff."""
    replay_input = {"chat_id": 1, "mode": "semantic", "system_version": "1.0"}
    expected = {"fragment": "x", "context": {}, "trace": {}, "explanation": {}}
    expected["signature"] = "exp_sig"
    actual = {"fragment": "y", "context": {}, "trace": {}, "explanation": {}}
    actual["signature"] = "act_sig"
    case = build_repro_case_from_failure(
        replay_input=replay_input,
        expected_result=expected,
        actual_result=actual,
    )
    assert case.metadata.failure_type == CONTEXT_DRIFT
    assert case.metadata.expected_signature == "exp_sig"
    assert case.metadata.actual_signature == "act_sig"


def test_persist_and_load_repro_case(tmp_path: Path) -> None:
    """Persist ReproCase, load it back. Deterministic JSON."""
    meta = FailureMetadata(
        failure_type=SIGNATURE_MISMATCH,
        drift_types=(),
        expected_signature="a",
        actual_signature="b",
    )
    case = ReproCase(
        replay_input={"chat_id": 1},
        expected_result={"fragment": "x", "signature": "a"},
        metadata=meta,
    )
    p = tmp_path / "repro.json"
    persist_repro_case(case, p)
    loaded = load_repro_case(p)
    assert loaded.replay_input == case.replay_input
    assert loaded.expected_result == case.expected_result
    assert loaded.metadata.failure_type == case.metadata.failure_type


def test_run_repro_case_passes_with_matching_input(tmp_path: Path) -> None:
    """run_repro_case passes when actual matches expected."""
    from app.context.replay.replay_service import get_context_replay_service

    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "replay_input_minimal.json"
    data = json.loads(fixture.read_text())
    replay_input = data
    svc = get_context_replay_service()
    result = svc.replay(
        dict_to_replay_input(replay_input),
        return_trace=True,
        return_fragment=True,
    )
    expected_result = result.to_dict()
    run_result = run_repro_case(replay_input, expected_result)
    record_repro_case_on_failure(
        replay_input,
        expected_result,
        run_result.actual_result,
        tmp_path / "repro_failures",
        msg="run_repro_case",
    )
    assert run_result.passed
    assert run_result.content_identical
    assert run_result.signature_match


def test_run_repro_case_from_file(tmp_path: Path) -> None:
    """run_repro_case_from_file loads, runs, compares."""
    from app.context.replay.replay_service import get_context_replay_service

    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "replay_input_minimal.json"
    data = json.loads(fixture.read_text())
    inp = dict_to_replay_input(data)
    svc = get_context_replay_service()
    res = svc.replay(inp, return_trace=True, return_fragment=True)
    expected = res.to_dict()
    case = ReproCase(
        replay_input=data,
        expected_result=expected,
        metadata=FailureMetadata(
            failure_type="",
            drift_types=(),
            expected_signature=expected["signature"],
            actual_signature=expected["signature"],
        ),
    )
    p = tmp_path / "repro.json"
    persist_repro_case(case, p)
    run_result = run_repro_case_from_file(p)
    record_repro_case_on_failure(
        data,
        expected,
        run_result.actual_result,
        tmp_path / "repro_failures",
        msg="run_repro_case_from_file",
    )
    assert run_result.passed
