"""
QA Autopilot v3 – Translation Gap Detection.

- incident without replay => incident_not_bound_to_replay
- incident without regression => incident_not_bound_to_regression
- pilot active but not reflected in backlog => pilot_not_sufficiently_translated
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import run_autopilot_v3


def _run_and_parse(fixtures_dir: Path, out_name: str = "out.json") -> dict:
    """Führt Autopilot aus und liefert geparstes Output."""
    out_path = fixtures_dir / out_name
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


def test_translation_incident_without_replay(translation_no_replay_fixtures_dir: Path) -> None:
    """Translation Gap: incident ohne replay_status => incident_not_bound_to_replay."""
    output = _run_and_parse(translation_no_replay_fixtures_dir, "out_tr_replay.json")
    translation_gaps = output.get("translation_gap_findings", [])
    no_replay = [g for g in translation_gaps if g.get("gap_type") == "incident_not_bound_to_replay"]
    assert len(no_replay) >= 1


def test_translation_incident_without_regression(translation_no_regression_fixtures_dir: Path) -> None:
    """Translation Gap: incident ohne Regression-Binding => incident_not_bound_to_regression."""
    output = _run_and_parse(translation_no_regression_fixtures_dir, "out_tr_regression.json")
    translation_gaps = output.get("translation_gap_findings", [])
    no_regression = [g for g in translation_gaps if g.get("gap_type") == "incident_not_bound_to_regression"]
    assert len(no_regression) >= 1


def test_translation_pilot_not_reflected(translation_pilot_fixtures_dir: Path) -> None:
    """Translation Gap: pilot aktiv, Fokus nicht in Top 3 => pilot_not_sufficiently_translated."""
    output = _run_and_parse(translation_pilot_fixtures_dir, "out_tr_pilot.json")
    translation_gaps = output.get("translation_gap_findings", [])
    pilot_gaps = [g for g in translation_gaps if g.get("gap_type") == "pilot_not_sufficiently_translated"]
    assert len(pilot_gaps) >= 1
