"""
QA Autopilot v3 – Happy Path Tests.

Gültige Inputs, QA_AUTOPILOT_V3.json wird erzeugt, summary und findings vorhanden.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import run_autopilot_v3


def _parse_first_json(text: str) -> dict:
    """Parst das erste JSON-Objekt aus stdout."""
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text)
    return obj


def test_happy_path_produces_output(autopilot_v3_fixtures_dir: Path) -> None:
    """Happy Path: gültige Inputs erzeugen QA_AUTOPILOT_V3.json."""
    out_path = autopilot_v3_fixtures_dir / "QA_AUTOPILOT_V3.json"
    trace_path = autopilot_v3_fixtures_dir / "trace.json"

    exit_code, _, _ = run_autopilot_v3(
        [
            "--input-incidents", str(autopilot_v3_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(autopilot_v3_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(autopilot_v3_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(autopilot_v3_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(autopilot_v3_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2026-01-01T00:00:00Z",
        ],
        cwd=autopilot_v3_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "schema_version" in output
    assert output["schema_version"] == "3.0"
    assert "generated_at" in output
    assert output["generated_at"] == "2026-01-01T00:00:00Z"


def test_happy_path_summary_present(autopilot_v3_fixtures_dir: Path) -> None:
    """Happy Path: summary ist vorhanden und enthält erwartete Keys."""
    out_path = autopilot_v3_fixtures_dir / "out.json"
    trace_path = autopilot_v3_fixtures_dir / "trace.json"

    exit_code, _, _ = run_autopilot_v3(
        [
            "--input-incidents", str(autopilot_v3_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(autopilot_v3_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(autopilot_v3_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(autopilot_v3_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(autopilot_v3_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2026-01-01T00:00:00Z",
        ],
        cwd=autopilot_v3_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    summary = output.get("summary", {})
    assert "total_test_gaps" in summary
    assert "total_guard_gaps" in summary
    assert "total_translation_gaps" in summary
    assert "recommended_backlog_count" in summary
    assert "high_priority_backlog_count" in summary


def test_happy_path_test_gap_findings_present(autopilot_v3_fixtures_dir: Path) -> None:
    """Happy Path: test_gap_findings ist Liste (kann leer sein)."""
    out_path = autopilot_v3_fixtures_dir / "out2.json"
    trace_path = autopilot_v3_fixtures_dir / "trace2.json"

    exit_code, _, _ = run_autopilot_v3(
        [
            "--input-incidents", str(autopilot_v3_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(autopilot_v3_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(autopilot_v3_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(autopilot_v3_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(autopilot_v3_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2026-01-01T00:00:00Z",
        ],
        cwd=autopilot_v3_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "test_gap_findings" in output
    assert isinstance(output["test_gap_findings"], list)


def test_happy_path_recommended_test_backlog_present(autopilot_v3_fixtures_dir: Path) -> None:
    """Happy Path: recommended_test_backlog ist vorhanden."""
    out_path = autopilot_v3_fixtures_dir / "out3.json"
    trace_path = autopilot_v3_fixtures_dir / "trace3.json"

    exit_code, _, _ = run_autopilot_v3(
        [
            "--input-incidents", str(autopilot_v3_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(autopilot_v3_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(autopilot_v3_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(autopilot_v3_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(autopilot_v3_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2026-01-01T00:00:00Z",
        ],
        cwd=autopilot_v3_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "recommended_test_backlog" in output
    assert isinstance(output["recommended_test_backlog"], list)


def test_happy_path_stdout_dry_run(autopilot_v3_fixtures_dir: Path) -> None:
    """Happy Path: --dry-run --output - liefert JSON auf stdout."""
    exit_code, stdout, _ = run_autopilot_v3(
        [
            "--input-incidents", str(autopilot_v3_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(autopilot_v3_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(autopilot_v3_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(autopilot_v3_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(autopilot_v3_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--dry-run",
            "--output", "-",
            "--trace-output", str(autopilot_v3_fixtures_dir / "trace_stdout.json"),
            "--timestamp", "2026-01-01T00:00:00Z",
        ],
        cwd=autopilot_v3_fixtures_dir,
    )

    assert exit_code == 0
    output = _parse_first_json(stdout)
    assert "summary" in output
    assert "test_gap_findings" in output
    assert "guard_gap_findings" in output
    assert "translation_gap_findings" in output
    assert "recommended_test_backlog" in output
