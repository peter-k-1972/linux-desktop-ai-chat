"""
Tests for repro failure helper.

Deterministic failure_id. No random. Reproducible.
"""

from pathlib import Path

import pytest

from tests.helpers.repro_failure_helper import (
    compute_failure_id,
    record_repro_case_on_failure,
)


def test_compute_failure_id_deterministic() -> None:
    """Same inputs => same failure_id. No random."""
    replay_input = {"chat_id": 1, "mode": "semantic"}
    expected = {"fragment": "x", "signature": "abc"}
    actual = {"fragment": "y", "signature": "def"}
    id1 = compute_failure_id(replay_input, expected, actual)
    id2 = compute_failure_id(replay_input, expected, actual)
    assert id1 == id2
    assert len(id1) == 16
    assert id1.isalnum()


def test_compute_failure_id_different_inputs_different_id() -> None:
    """Different inputs => different failure_id."""
    replay_input = {"chat_id": 1}
    expected = {"signature": "a"}
    actual = {"signature": "b"}
    id1 = compute_failure_id(replay_input, expected, actual)
    id2 = compute_failure_id({"chat_id": 2}, expected, actual)
    assert id1 != id2


def test_record_repro_case_on_failure_persists(tmp_path: Path) -> None:
    """On failure, repro case is persisted with deterministic failure_id."""
    replay_input = {"chat_id": 1, "mode": "semantic", "system_version": "1.0"}
    expected = {"fragment": "x", "context": {}, "trace": {}, "explanation": {}, "signature": "exp"}
    actual = {"fragment": "y", "context": {}, "trace": {}, "explanation": {}, "signature": "act"}
    output_dir = tmp_path / "repro_failures"

    with pytest.raises(AssertionError, match="FAIL"):
        record_repro_case_on_failure(
            replay_input,
            expected,
            actual,
            output_dir,
            msg="test",
        )

    failure_id = compute_failure_id(replay_input, expected, actual)
    persisted = output_dir / f"{failure_id}.json"
    assert persisted.exists()
    import json
    data = json.loads(persisted.read_text())
    assert data["replay_input"]["chat_id"] == 1
    assert data["expected_result"]["fragment"] == "x"
    assert data["metadata"]["expected_signature"] == "exp"
    assert data["metadata"]["actual_signature"] == "act"


def test_record_repro_case_on_success_no_persist(tmp_path: Path) -> None:
    """On success, no file is persisted."""
    replay_input = {"chat_id": 1}
    expected = {"fragment": "x", "context": {}, "trace": {}, "explanation": {}, "signature": "s"}
    actual = {"fragment": "x", "context": {}, "trace": {}, "explanation": {}, "signature": "s"}
    output_dir = tmp_path / "repro_failures"

    record_repro_case_on_failure(
        replay_input,
        expected,
        actual,
        output_dir,
        msg="test",
    )

    assert not output_dir.exists() or len(list(output_dir.glob("*.json"))) == 0
