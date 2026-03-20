"""
Tests for context replay CLI.

No UI. No logging side effects. Deterministic output only.
"""

import json
from pathlib import Path

import pytest

from app.cli.context_replay import run_replay


def test_run_replay_produces_json(tmp_path: Path) -> None:
    """run_replay loads JSON, runs replay, returns valid JSON."""
    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "replay_input_minimal.json"
    output = run_replay(fixture)
    parsed = json.loads(output)
    assert "fragment" in parsed
    assert "context" in parsed
    assert "trace" in parsed
    assert "explanation" in parsed


def test_run_replay_deterministic(tmp_path: Path) -> None:
    """run_replay produces identical output for identical input."""
    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "replay_input_minimal.json"
    out1 = run_replay(fixture)
    out2 = run_replay(fixture)
    assert out1 == out2


def test_run_replay_file_not_found() -> None:
    """run_replay raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError, match="not found"):
        run_replay("/nonexistent/path.json")


def test_run_replay_version_mismatch_raises(tmp_path: Path) -> None:
    """run_replay raises ReplayVersionMismatchError when system_version is wrong."""
    from app.context.replay.replay_models import ReplayVersionMismatchError

    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "replay_input_minimal.json"
    data = json.loads(fixture.read_text())
    data["system_version"] = "0.9"
    wrong_file = tmp_path / "wrong_version.json"
    wrong_file.write_text(json.dumps(data))

    with pytest.raises(ReplayVersionMismatchError, match="version mismatch"):
        run_replay(wrong_file)
