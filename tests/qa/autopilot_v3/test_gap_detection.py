"""
QA Autopilot v3 – Test Gap und Guard Gap Detection.

- replay gap => missing_replay_test
- regression gap => missing_regression_test
- drift => missing_contract_test
- network failure => failure_replay_guard
- event drift => event_contract_guard
- startup unreachable => startup_degradation_guard
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


def test_replay_gap_missing_replay_test(replay_gap_fixtures_dir: Path) -> None:
    """Test Gap: replay gap >= 50% + 2+ Incidents => missing_replay_test."""
    output = _run_and_parse(replay_gap_fixtures_dir, "out_replay.json")
    test_gaps = output.get("test_gap_findings", [])
    missing_replay = [g for g in test_gaps if g.get("gap_type") == "missing_replay_test"]
    assert len(missing_replay) >= 1
    assert any("replay" in str(g.get("reasons", [])).lower() for g in missing_replay)


def test_regression_gap_missing_regression_test(regression_gap_fixtures_dir: Path) -> None:
    """Test Gap: regression gap >= 30% + 2+ Incidents => missing_regression_test."""
    output = _run_and_parse(regression_gap_fixtures_dir, "out_regression.json")
    test_gaps = output.get("test_gap_findings", [])
    missing_regression = [g for g in test_gaps if g.get("gap_type") == "missing_regression_test"]
    assert len(missing_regression) >= 1
    assert any("regression" in str(g.get("reasons", [])).lower() for g in missing_regression)


def test_drift_missing_contract_test(drift_gap_fixtures_dir: Path) -> None:
    """Test Gap: 2+ Drift-Incidents => missing_contract_test."""
    output = _run_and_parse(drift_gap_fixtures_dir, "out_drift.json")
    test_gaps = output.get("test_gap_findings", [])
    missing_contract = [g for g in test_gaps if g.get("gap_type") == "missing_contract_test"]
    assert len(missing_contract) >= 1
    assert any("drift" in str(g.get("reasons", [])).lower() for g in missing_contract)


def test_guard_network_failure_replay_guard(guard_network_fixtures_dir: Path) -> None:
    """Guard Gap: 2+ network failure incidents => failure_replay_guard."""
    output = _run_and_parse(guard_network_fixtures_dir, "out_guard_net.json")
    guard_gaps = output.get("guard_gap_findings", [])
    failure_replay = [g for g in guard_gaps if g.get("guard_type") == "failure_replay_guard"]
    assert len(failure_replay) >= 1


def test_guard_event_drift_event_contract_guard(guard_event_drift_fixtures_dir: Path) -> None:
    """Guard Gap: 1+ event/contract drift => event_contract_guard."""
    output = _run_and_parse(guard_event_drift_fixtures_dir, "out_guard_event.json")
    guard_gaps = output.get("guard_gap_findings", [])
    event_contract = [g for g in guard_gaps if g.get("guard_type") == "event_contract_guard"]
    assert len(event_contract) >= 1


def test_guard_startup_degradation_guard(guard_startup_fixtures_dir: Path) -> None:
    """Guard Gap: 1+ startup degradation => startup_degradation_guard."""
    output = _run_and_parse(guard_startup_fixtures_dir, "out_guard_startup.json")
    guard_gaps = output.get("guard_gap_findings", [])
    startup_guard = [g for g in guard_gaps if g.get("guard_type") == "startup_degradation_guard"]
    assert len(startup_guard) >= 1
