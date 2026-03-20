"""
QA Autopilot v3 – Recommended Test Backlog.

- priorisierte Vorschläge
- reasons vorhanden
- priority plausibel
- Struktur stabil
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import run_autopilot_v3


def _run_and_parse(fixtures_dir: Path) -> dict:
    """Führt Autopilot aus und liefert geparstes Output."""
    out_path = fixtures_dir / "out_backlog.json"
    trace_path = fixtures_dir / "trace.json"
    exit_code, _, _ = run_autopilot_v3(
        [
            "--input-incidents", str(fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2026-01-01T00:00:00Z",
        ],
        cwd=fixtures_dir,
    )
    assert exit_code == 0
    return json.loads(out_path.read_text(encoding="utf-8"))


def test_backlog_contains_prioritized_items(guard_event_drift_fixtures_dir: Path) -> None:
    """Backlog enthält priorisierte Vorschläge mit priority-Feld."""
    output = _run_and_parse(guard_event_drift_fixtures_dir)
    backlog = output.get("recommended_test_backlog", [])
    assert len(backlog) >= 1
    for item in backlog:
        assert "priority" in item
        assert item["priority"] in ("high", "medium", "low")


def test_backlog_items_have_reasons(guard_event_drift_fixtures_dir: Path) -> None:
    """Backlog-Items haben reasons."""
    output = _run_and_parse(guard_event_drift_fixtures_dir)
    backlog = output.get("recommended_test_backlog", [])
    for item in backlog:
        assert "reasons" in item
        assert isinstance(item["reasons"], list)


def test_backlog_structure_stable(autopilot_v3_fixtures_dir: Path) -> None:
    """Backlog-Items haben stabile Struktur: id, title, subsystem, failure_class, test_domain, test_type, guard_type."""
    out_path = autopilot_v3_fixtures_dir / "out_struct.json"
    trace_path = autopilot_v3_fixtures_dir / "trace_struct.json"
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
    backlog = output.get("recommended_test_backlog", [])
    required_keys = {"id", "title", "subsystem", "failure_class", "test_domain", "test_type", "guard_type", "priority", "reasons"}
    for item in backlog:
        for key in required_keys:
            assert key in item, f"Backlog-Item fehlt Key: {key}"
