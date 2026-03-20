"""
CLI/IO Tests: Generatoren.

Testet --output -, invalid JSON, fehlende Dateien, Trace-Inhalt.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import run_generator_script


def _parse_first_json(text: str) -> dict:
    """Parst das erste JSON-Objekt aus stdout (Skripte drucken danach weitere Zeilen)."""
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text)
    return obj


def test_out_stdout_cc(generator_fixtures_dir: Path) -> None:
    """OUT-Stdout: --output - bei Control Center liefert JSON auf stdout."""
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace_stdout.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(generator_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", "-",
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = _parse_first_json(stdout)
    assert "current_focus" in output
    assert trace_path.exists()


def test_out_stdout_ps(generator_fixtures_dir: Path) -> None:
    """OUT-Stdout: --output - bei Priority Scores."""
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace_ps_stdout.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_priority_scores.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", "-",
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = _parse_first_json(stdout)
    assert "subsystem_scores" in output
    assert trace_path.exists()


def test_out_stdout_rr(generator_fixtures_dir: Path) -> None:
    """OUT-Stdout: --output - bei Risk Radar."""
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace_rr_stdout.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_risk_radar.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-risk-radar", str(generator_fixtures_dir / "QA_RISK_RADAR.md"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", "-",
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = _parse_first_json(stdout)
    assert "subsystems" in output
    assert trace_path.exists()


def test_trace_content_cc(generator_fixtures_dir: Path) -> None:
    """TRACE-Content: Trace enthält generated_at, generator, input_sources, applied_rules."""
    out_path = generator_fixtures_dir / "QA_CC_OUT.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace_content.json"

    exit_code, _, _ = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(generator_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert "generated_at" in trace
    assert "generator" in trace
    assert "input_sources" in trace
    assert "applied_rules" in trace
    assert "summary" in trace


def test_invalid_json_incidents(generator_fixtures_dir: Path) -> None:
    """INVALID-JSON: Kaputte incidents/index.json führt zu kontrollierter Reaktion."""
    bad_index = generator_fixtures_dir / "incidents" / "index.json"
    bad_index.write_text("{invalid json}", encoding="utf-8")

    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(bad_index),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(generator_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--output", str(generator_fixtures_dir / "out.json"),
            "--trace-output", str(generator_fixtures_dir / "trace.json"),
        ],
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads((generator_fixtures_dir / "out.json").read_text(encoding="utf-8"))
    assert "global_warnings" in output or "warnings" in output
    assert any("incidents" in w.lower() for w in (output.get("global_warnings") or output.get("warnings") or []))


def test_cli_custom_paths(generator_fixtures_dir: Path) -> None:
    """CLI-Input-Paths: Custom Pfade werden korrekt geladen."""
    out_path = generator_fixtures_dir / "custom_out.json"
    trace_path = generator_fixtures_dir / "custom_trace.json"

    exit_code, _, _ = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(generator_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(generator_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(generator_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(generator_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(generator_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "input_sources" in output
    assert len(output["input_sources"]) >= 3
