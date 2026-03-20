"""
Acceptance Tests: update_priority_scores.py.

Blocking acceptance tests from QA_FEEDBACK_LOOP_ACCEPTANCE_CHECKLIST:
- HP-PS-Full: Happy Path Priority Scores
- DRY-PS: Dry-run write-free
- MISS-Both-PS: Weder QA_PRIORITY_SCORE noch incidents → Exit 1
- CAP-Delta-PS: Max-Delta-Capping (new_score - old_score ≤ 10)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import ACCEPTANCE_TIMESTAMP, run_generator_script


def _ps_args(fixtures_dir: Path, out_path: Path | None = None, trace_path: Path | None = None) -> list[str]:
    inc_dir = fixtures_dir / "incidents"
    base = [
        "--input-incidents", str(inc_dir / "index.json"),
        "--input-analytics", str(inc_dir / "analytics.json"),
        "--input-autopilot", str(fixtures_dir / "QA_AUTOPILOT_V2.json"),
        "--input-priority-score", str(fixtures_dir / "QA_PRIORITY_SCORE.json"),
        "--timestamp", ACCEPTANCE_TIMESTAMP,
    ]
    if out_path is not None:
        base.extend(["--output", str(out_path)])
    if trace_path is not None:
        base.extend(["--trace-output", str(trace_path)])
    return base


# -----------------------------------------------------------------------------
# HP-PS-Full: Happy Path Priority Scores
# -----------------------------------------------------------------------------


def test_hp_ps_full(acceptance_fixtures_dir: Path) -> None:
    """HP-PS-Full: Alle Dateien vorhanden → Exit 0; scores[], subsystem_scores, failure_class_scores."""
    out_path = acceptance_fixtures_dir / "QA_PRIORITY_SCORE.json"
    trace_path = acceptance_fixtures_dir / "feedback_loop" / "priority_score_feedback_trace.json"

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(acceptance_fixtures_dir, out_path, trace_path),
        cwd=acceptance_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    assert trace_path.exists()

    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "scores" in output
    assert "subsystem_scores" in output
    assert "failure_class_scores" in output
    assert output["generated_at"] == ACCEPTANCE_TIMESTAMP
    assert len(output["subsystem_scores"]) >= 1
    assert len(output["scores"]) >= 1


# -----------------------------------------------------------------------------
# DRY-PS: Dry-run Priority Scores
# -----------------------------------------------------------------------------


def test_dry_ps(acceptance_fixtures_dir: Path) -> None:
    """DRY-PS: --dry-run; alle Inputs vorhanden → Exit 0; keine Datei geschrieben."""
    out_path = acceptance_fixtures_dir / "OUT_DRY_PS.json"
    trace_path = acceptance_fixtures_dir / "feedback_loop" / "trace_ps_dry.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_priority_scores.py",
        _ps_args(acceptance_fixtures_dir, out_path, trace_path) + ["--dry-run"],
        cwd=acceptance_fixtures_dir,
    )

    assert exit_code == 0
    assert not out_path.exists()
    assert not trace_path.exists()

    output = json.loads(stdout)
    assert "subsystem_scores" in output
    assert "suppressed_changes" in output


# -----------------------------------------------------------------------------
# MISS-Both-PS: Fehlende Baseline (Priority Scores)
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# OUT-Stdout: Output auf stdout
# -----------------------------------------------------------------------------


def test_out_stdout_ps(acceptance_fixtures_dir: Path) -> None:
    """OUT-Stdout: --output - liefert JSON auf stdout; Trace-Datei trotzdem geschrieben."""
    trace_path = acceptance_fixtures_dir / "feedback_loop" / "trace_ps_stdout.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_priority_scores.py",
        [
            "--input-incidents", str(acceptance_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(acceptance_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(acceptance_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-priority-score", str(acceptance_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", "-",
            "--trace-output", str(trace_path),
            "--timestamp", ACCEPTANCE_TIMESTAMP,
        ],
        cwd=acceptance_fixtures_dir,
    )

    assert exit_code == 0
    decoder = json.JSONDecoder()
    output, _ = decoder.raw_decode(stdout)
    assert "subsystem_scores" in output
    assert trace_path.exists()


# -----------------------------------------------------------------------------
# MISS-Both-PS: Fehlende Baseline (Priority Scores)
# -----------------------------------------------------------------------------


def test_miss_both_ps(no_priority_no_incidents_fixtures_dir: Path) -> None:
    """MISS-Both-PS: Weder QA_PRIORITY_SCORE noch incidents → Exit 1."""
    inc_dir = no_priority_no_incidents_fixtures_dir / "incidents"

    exit_code, stdout, stderr = run_generator_script(
        "update_priority_scores.py",
        [
            "--input-incidents", str(inc_dir / "index.json"),
            "--input-analytics", str(inc_dir / "analytics.json"),
            "--input-autopilot", str(no_priority_no_incidents_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-priority-score", str(no_priority_no_incidents_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(no_priority_no_incidents_fixtures_dir / "out.json"),
            "--trace-output", str(no_priority_no_incidents_fixtures_dir / "trace.json"),
            "--timestamp", ACCEPTANCE_TIMESTAMP,
        ],
        cwd=no_priority_no_incidents_fixtures_dir,
    )

    assert exit_code == 1
    assert "Weder" in stderr or "fehlt" in stderr.lower() or "gefunden" in stderr.lower()


# -----------------------------------------------------------------------------
# CAP-Delta-PS: Max-Delta-Capping
# -----------------------------------------------------------------------------


def test_cap_delta_ps(cap_delta_fixtures_dir: Path) -> None:
    """CAP-Delta-PS: raw_delta > 10 → new_score - old_score ≤ 10; suppressed_changes dokumentiert."""
    out_path = cap_delta_fixtures_dir / "OUT_PS.json"
    trace_path = cap_delta_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(cap_delta_fixtures_dir, out_path, trace_path),
        cwd=cap_delta_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert output["score_policy"]["max_delta_per_run"] == 10

    for sub, data in output.get("subsystem_scores", {}).items():
        delta = data.get("delta", 0)
        assert abs(delta) <= 10, f"Delta für {sub} überschreitet 10: {delta}"

    suppressed = output.get("suppressed_changes", [])
    if suppressed:
        for s in suppressed:
            assert "subsystem" in s
            assert "raw_delta" in s
            assert "capped_delta" in s
            assert abs(s["capped_delta"]) <= 10
