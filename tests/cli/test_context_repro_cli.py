"""
Tests for context repro CLI tools.

Deterministic output. No UI. sort_keys=True.
"""

import json
from pathlib import Path

import pytest

from app.cli.context_repro_run import run_repro
from app.cli.context_repro_batch import run_repro_batch


def test_context_repro_run_produces_json() -> None:
    """run_repro produces valid JSON with expected keys."""
    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "repro_case_minimal.json"
    output = run_repro(fixture)
    parsed = json.loads(output)
    assert "passed" in parsed
    assert "content_identical" in parsed
    assert "signature_match" in parsed
    assert "drift_types" in parsed
    assert "file" in parsed


def test_context_repro_run_deterministic() -> None:
    """run_repro produces identical output for identical input."""
    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "repro_case_minimal.json"
    out1 = run_repro(fixture)
    out2 = run_repro(fixture)
    assert out1 == out2


def test_context_repro_run_file_not_found() -> None:
    """run_repro raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError, match="not found"):
        run_repro("/nonexistent/repro.json")


def test_context_repro_batch_produces_json(tmp_path: Path) -> None:
    """run_repro_batch produces valid JSON with results list."""
    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "repro_case_minimal.json"
    import shutil
    shutil.copy(fixture, tmp_path / "repro1.json")
    output = run_repro_batch(tmp_path)
    parsed = json.loads(output)
    assert "results" in parsed
    assert "total" in parsed
    assert "passed" in parsed
    assert isinstance(parsed["results"], list)
    assert len(parsed["results"]) == 1


def test_context_repro_batch_sorted_files(tmp_path: Path) -> None:
    """run_repro_batch processes files in sorted order (a before z)."""
    import shutil

    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "repro_case_minimal.json"
    shutil.copy(fixture, tmp_path / "z_repro.json")
    shutil.copy(fixture, tmp_path / "a_repro.json")
    output = run_repro_batch(tmp_path)
    parsed = json.loads(output)
    files = [Path(r["file"]).name for r in parsed["results"]]
    assert files == ["a_repro.json", "z_repro.json"]


def test_context_repro_batch_dir_not_found() -> None:
    """run_repro_batch raises FileNotFoundError for missing directory."""
    with pytest.raises(FileNotFoundError, match="not found"):
        run_repro_batch("/nonexistent/dir")
