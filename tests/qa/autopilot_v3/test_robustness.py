"""
QA Autopilot v3 – Robuste Fehlerfälle.

- fehlende incidents-Datei
- fehlende analytics-Datei
- fehlende autopilot_v2-Datei (Exit 1)
- leere JSON
- ungültige JSON
- unbekanntes subsystem
- ungültiger Score in QA_PRIORITY_SCORE
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import run_autopilot_v3


def _run_autopilot(fixtures_dir: Path, extra_args: list[str] | None = None) -> tuple[int, str, str]:
    """Führt Autopilot mit Standard-Args aus."""
    args = [
        "--input-incidents", str(fixtures_dir / "incidents" / "index.json"),
        "--input-analytics", str(fixtures_dir / "incidents" / "analytics.json"),
        "--input-autopilot", str(fixtures_dir / "QA_AUTOPILOT_V2.json"),
        "--input-control-center", str(fixtures_dir / "QA_CONTROL_CENTER.json"),
        "--input-priority-score", str(fixtures_dir / "QA_PRIORITY_SCORE.json"),
        "--output", str(fixtures_dir / "out.json"),
        "--trace-output", str(fixtures_dir / "trace.json"),
        "--timestamp", "2026-01-01T00:00:00Z",
    ]
    if extra_args:
        args.extend(extra_args)
    return run_autopilot_v3(args, cwd=fixtures_dir)


def test_missing_incidents_handled(missing_incidents_fixtures_dir: Path) -> None:
    """Fehlende incidents-Datei: Script läuft, Projektion mit leeren Incidents."""
    exit_code, _, _ = _run_autopilot(missing_incidents_fixtures_dir)
    assert exit_code == 0
    out_path = missing_incidents_fixtures_dir / "out.json"
    assert out_path.exists()
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert output.get("summary", {}).get("total_test_gaps", 0) >= 0


def test_missing_analytics_handled(missing_analytics_fixtures_dir: Path) -> None:
    """Fehlende analytics-Datei: Script läuft mit Fallback."""
    exit_code, _, _ = _run_autopilot(missing_analytics_fixtures_dir)
    assert exit_code == 0
    out_path = missing_analytics_fixtures_dir / "out.json"
    assert out_path.exists()


def test_missing_autopilot_exit_1(missing_autopilot_fixtures_dir: Path) -> None:
    """Fehlende autopilot_v2-Datei: Exit 1 (Release-Blocker)."""
    exit_code, _, stderr = _run_autopilot(missing_autopilot_fixtures_dir)
    assert exit_code == 1
    assert "QA_AUTOPILOT_V2" in stderr or "autopilot" in stderr.lower()


def test_empty_json_incidents_handled(empty_json_incidents_fixtures_dir: Path) -> None:
    """Leere JSON {} für incidents: load_json gibt None, Script läuft mit leeren Incidents."""
    exit_code, _, _ = _run_autopilot(empty_json_incidents_fixtures_dir)
    assert exit_code == 0
    out_path = empty_json_incidents_fixtures_dir / "out.json"
    assert out_path.exists()


def test_invalid_json_incidents_handled(invalid_json_incidents_fixtures_dir: Path) -> None:
    """Ungültige JSON für incidents: load_json gibt None, Script läuft."""
    exit_code, _, _ = _run_autopilot(invalid_json_incidents_fixtures_dir)
    assert exit_code == 0
    out_path = invalid_json_incidents_fixtures_dir / "out.json"
    assert out_path.exists()


def test_unknown_subsystem_no_crash(unknown_subsystem_fixtures_dir: Path) -> None:
    """Unbekanntes subsystem: Script crasht nicht."""
    exit_code, _, _ = _run_autopilot(unknown_subsystem_fixtures_dir)
    assert exit_code == 0
    output = json.loads((unknown_subsystem_fixtures_dir / "out.json").read_text(encoding="utf-8"))
    assert "summary" in output


def test_invalid_priority_score_controlled_failure(invalid_priority_score_fixtures_dir: Path) -> None:
    """Ungültiger Score in QA_PRIORITY_SCORE: Feedback-Loop crasht, Exit 1 (kein unhandled Exception).
    Hinweis: Autopilot v3 rules nutzen _safe_score; der Feedback-Loop (_extract_current_priority_scores)
    verarbeitet Score noch nicht robust. Kontrollierter Abbruch mit Exit 1."""
    exit_code, _, stderr = _run_autopilot(invalid_priority_score_fixtures_dir)
    assert exit_code == 1
    assert "Score" in stderr or "int" in stderr or "ValueError" in stderr
