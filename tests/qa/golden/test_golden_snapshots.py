"""
Golden-/Snapshot-Tests für QA Feedback Loop Generatoren.

Sichert deterministische und diff-freundliche Outputs bei gleichen Inputs.
Vergleicht Generator-Ausgaben gegen committete Golden-Dateien.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.qa.generators.conftest import run_generator_script

# Golden-Dateien relativ zu diesem Modul
_GOLDEN_DIR = Path(__file__).resolve().parent / "expected"
_TIMESTAMP = "2025-01-15T12:00:00Z"


def _extract_trace_from_stderr(stderr: str) -> str:
    """Extrahiert Trace-JSON aus stderr (nach '--- TRACE ---')."""
    if "--- TRACE ---" in stderr:
        return stderr.split("--- TRACE ---", 1)[1].strip()
    return stderr.strip()


def _load_golden(name: str) -> dict:
    """Lädt Golden-JSON."""
    path = _GOLDEN_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_json_equal(actual: dict, expected: dict, exclude_keys: tuple[str, ...] = ()) -> None:
    """Vergleicht JSON-Strukturen, optional mit ausgeschlossenen Keys."""
    a = {k: v for k, v in actual.items() if k not in exclude_keys}
    e = {k: v for k, v in expected.items() if k not in exclude_keys}
    assert a == e, f"JSON differs:\nActual keys: {sorted(a.keys())}\nExpected keys: {sorted(e.keys())}"


# -----------------------------------------------------------------------------
# 1. Control Center Output
# -----------------------------------------------------------------------------


def test_golden_control_center_output(generator_fixtures_dir: Path) -> None:
    """Control Center: stabiler JSON-Inhalt bei gleichen Inputs."""
    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(generator_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--dry-run",
            "--timestamp", _TIMESTAMP,
        ],
        cwd=generator_fixtures_dir,
    )
    assert exit_code == 0
    actual = json.loads(stdout)
    expected = _load_golden("control_center")
    _assert_json_equal(actual, expected)


# -----------------------------------------------------------------------------
# 2. Priority Score Output
# -----------------------------------------------------------------------------


def test_golden_priority_score_output(generator_fixtures_dir: Path) -> None:
    """Priority Score: stabile Score-Struktur, Reihenfolge, Gründe, Regel-IDs."""
    exit_code, stdout, stderr = run_generator_script(
        "update_priority_scores.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--dry-run",
            "--timestamp", _TIMESTAMP,
        ],
        cwd=generator_fixtures_dir,
    )
    assert exit_code == 0
    actual = json.loads(stdout)
    expected = _load_golden("priority_score")
    _assert_json_equal(actual, expected)


# -----------------------------------------------------------------------------
# 3. Risk Radar Output
# -----------------------------------------------------------------------------


def test_golden_risk_radar_output(generator_fixtures_dir: Path) -> None:
    """Risk Radar: stabile Risikoprojektion, Marker, Reasons, Escalations."""
    exit_code, stdout, stderr = run_generator_script(
        "update_risk_radar.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-risk-radar", str(generator_fixtures_dir / "QA_RISK_RADAR.md"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--dry-run",
            "--timestamp", _TIMESTAMP,
        ],
        cwd=generator_fixtures_dir,
    )
    assert exit_code == 0
    actual = json.loads(stdout)
    expected = _load_golden("risk_radar")
    _assert_json_equal(actual, expected)


# -----------------------------------------------------------------------------
# 4. Trace-Dateien
# -----------------------------------------------------------------------------


def test_golden_control_center_trace(generator_fixtures_dir: Path) -> None:
    """Control Center Trace: Pflichtfelder stabil, keine Strukturdrift."""
    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(generator_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--dry-run",
            "--timestamp", _TIMESTAMP,
        ],
        cwd=generator_fixtures_dir,
    )
    assert exit_code == 0
    trace_str = _extract_trace_from_stderr(stderr)
    actual = json.loads(trace_str)
    expected = _load_golden("control_center_trace")
    _assert_json_equal(actual, expected)


def test_golden_priority_score_trace(generator_fixtures_dir: Path) -> None:
    """Priority Score Trace: Pflichtfelder stabil."""
    exit_code, stdout, stderr = run_generator_script(
        "update_priority_scores.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--dry-run",
            "--timestamp", _TIMESTAMP,
        ],
        cwd=generator_fixtures_dir,
    )
    assert exit_code == 0
    trace_str = _extract_trace_from_stderr(stderr)
    actual = json.loads(trace_str)
    expected = _load_golden("priority_score_trace")
    _assert_json_equal(actual, expected)


def test_golden_risk_radar_trace(generator_fixtures_dir: Path) -> None:
    """Risk Radar Trace: Pflichtfelder stabil."""
    exit_code, stdout, stderr = run_generator_script(
        "update_risk_radar.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-risk-radar", str(generator_fixtures_dir / "QA_RISK_RADAR.md"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--dry-run",
            "--timestamp", _TIMESTAMP,
        ],
        cwd=generator_fixtures_dir,
    )
    assert exit_code == 0
    trace_str = _extract_trace_from_stderr(stderr)
    actual = json.loads(trace_str)
    expected = _load_golden("risk_radar_trace")
    _assert_json_equal(actual, expected)


# -----------------------------------------------------------------------------
# 5. generated_at / Zeitfelder
# -----------------------------------------------------------------------------


def test_golden_generated_at_normalized() -> None:
    """generated_at ist in Golden-Dateien auf festen Wert normalisiert (transparent)."""
    for name in ("control_center", "priority_score", "risk_radar"):
        data = _load_golden(name)
        assert data.get("generated_at") == _TIMESTAMP, f"{name}: generated_at nicht normalisiert"
