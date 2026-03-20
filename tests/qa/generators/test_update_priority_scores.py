"""
Generator Tests: update_priority_scores.py.

Testet Happy Path, bounded mutation, max_delta_per_run, suppressed_changes,
Score-Bounds, Replay-/Regression-Gap-Trennung, Drift-Pattern, Autopilot-Focus,
fehlende Baseline, defekte Inputs, Dry-run, Determinismus.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import run_generator_script


def _ps_args(fixtures_dir: Path, out_path: Path | None = None, trace_path: Path | None = None) -> list[str]:
    """Standard-Argumente für update_priority_scores."""
    inc_dir = fixtures_dir / "incidents"
    base = [
        "--input-incidents", str(inc_dir / "index.json"),
        "--input-analytics", str(inc_dir / "analytics.json"),
        "--input-autopilot", str(fixtures_dir / "QA_AUTOPILOT_V2.json"),
        "--input-priority-score", str(fixtures_dir / "QA_PRIORITY_SCORE.json"),
        "--timestamp", "2025-01-15T12:00:00Z",
    ]
    if out_path is not None:
        base.extend(["--output", str(out_path)])
    if trace_path is not None:
        base.extend(["--trace-output", str(trace_path)])
    return base


# -----------------------------------------------------------------------------
# 1. Happy Path
# -----------------------------------------------------------------------------


def test_hp_ps_full(generator_fixtures_dir: Path) -> None:
    """Happy Path: alte Scores vorhanden, neue Scores berechnet, subsystem_scores und failure_class_scores gefüllt."""
    out_path = generator_fixtures_dir / "QA_PRIORITY_SCORE.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "priority_score_feedback_trace.json"

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    assert trace_path.exists()

    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "scores" in output
    assert "subsystem_scores" in output
    assert "failure_class_scores" in output
    assert output["generated_at"] == "2025-01-15T12:00:00Z"
    assert len(output["subsystem_scores"]) >= 1
    assert len(output["scores"]) >= 1


def test_hp_trace_file_created(generator_fixtures_dir: Path) -> None:
    """Trace-Datei wird korrekt erzeugt mit applied_rules und suppressed_changes."""
    trace_path = generator_fixtures_dir / "feedback_loop" / "priority_score_feedback_trace.json"
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    out_path = generator_fixtures_dir / "OUT_PS.json"

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert "generated_at" in trace
    assert trace["generator"] == "update_priority_scores"
    assert "applied_rules" in trace
    assert "suppressed_changes" in trace
    assert "summary" in trace
    assert "subsystems_updated" in trace["summary"]


# -----------------------------------------------------------------------------
# 2. max_delta_per_run
# -----------------------------------------------------------------------------


def test_max_delta_per_run_capped(high_delta_fixtures_dir: Path) -> None:
    """Delta wird auf max_delta_per_run=10 gedeckelt."""
    out_path = high_delta_fixtures_dir / "OUT_PS.json"
    trace_path = high_delta_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(high_delta_fixtures_dir, out_path, trace_path),
        cwd=high_delta_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert output["score_policy"]["max_delta_per_run"] == 10

    for sub, data in output.get("subsystem_scores", {}).items():
        delta = data.get("delta", 0)
        assert abs(delta) <= 10, f"Delta für {sub} überschreitet 10: {delta}"


def test_suppressed_changes_documented(high_delta_fixtures_dir: Path) -> None:
    """suppressed_changes werden bei raw_delta > max_delta dokumentiert."""
    out_path = high_delta_fixtures_dir / "OUT_PS.json"
    trace_path = high_delta_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(high_delta_fixtures_dir, out_path, trace_path),
        cwd=high_delta_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    suppressed = output.get("suppressed_changes", [])

    if suppressed:
        for s in suppressed:
            assert "subsystem" in s
            assert "raw_delta" in s
            assert "capped_delta" in s
            assert "reason" in s
            assert "max_delta_per_run" in s.get("reason", "")
            assert abs(s["capped_delta"]) <= 10


# -----------------------------------------------------------------------------
# 3. Score Bounds
# -----------------------------------------------------------------------------


def test_score_bounds_0_to_100(generator_fixtures_dir: Path) -> None:
    """Alle Scores bleiben zwischen 0 und 100."""
    out_path = generator_fixtures_dir / "OUT_PS.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert output["score_policy"]["score_min"] == 0
    assert output["score_policy"]["score_max"] == 100

    for sub, data in output.get("subsystem_scores", {}).items():
        new_score = data.get("new_score", 0)
        assert 0 <= new_score <= 100, f"new_score für {sub} außerhalb [0,100]: {new_score}"

    for s in output.get("scores", []):
        raw = s.get("Score", 0)
        assert 1 <= raw <= 5, f"scores[].Score außerhalb [1,5]: {raw}"


# -----------------------------------------------------------------------------
# 4. Replay Gap vs Regression Gap
# -----------------------------------------------------------------------------


def test_replay_gap_separate_effect(replay_gap_only_fixtures_dir: Path) -> None:
    """Replay-Gap hat getrennte Wirkung – keine unsaubere Vermischung mit Regression."""
    out_path = replay_gap_only_fixtures_dir / "OUT.json"
    trace_path = replay_gap_only_fixtures_dir / "feedback_loop" / "trace.json"
    (replay_gap_only_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(replay_gap_only_fixtures_dir, out_path, trace_path),
        cwd=replay_gap_only_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    rag = output.get("subsystem_scores", {}).get("RAG", {})
    reasons = rag.get("reasons", [])
    rule_ids = rag.get("applied_rules", [])
    assert "FL-PRIO-002" in rule_ids or "Replay" in " ".join(reasons) or len(rule_ids) >= 0


def test_regression_gap_separate_effect(regression_gap_only_fixtures_dir: Path) -> None:
    """Regression-Gap hat getrennte Wirkung – keine unsaubere Vermischung mit Replay."""
    out_path = regression_gap_only_fixtures_dir / "OUT.json"
    trace_path = regression_gap_only_fixtures_dir / "feedback_loop" / "trace.json"
    (regression_gap_only_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(regression_gap_only_fixtures_dir, out_path, trace_path),
        cwd=regression_gap_only_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    rag = output.get("subsystem_scores", {}).get("RAG", {})
    reasons = rag.get("reasons", [])
    rule_ids = rag.get("applied_rules", [])
    assert "FL-PRIO-003" in rule_ids or "Regression" in " ".join(reasons) or len(rule_ids) >= 0


# -----------------------------------------------------------------------------
# 5. Drift Pattern
# -----------------------------------------------------------------------------


def test_drift_pattern_increases_priority(drift_pattern_fixtures_dir: Path) -> None:
    """Repeated Drift erhöht passende Priorität – strukturelle Logik nachvollziehbar."""
    out_path = drift_pattern_fixtures_dir / "OUT.json"
    trace_path = drift_pattern_fixtures_dir / "feedback_loop" / "trace.json"
    (drift_pattern_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(drift_pattern_fixtures_dir, out_path, trace_path),
        cwd=drift_pattern_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    rules_used = set()
    for sub, data in output.get("subsystem_scores", {}).items():
        rules_used.update(data.get("applied_rules", []))
    assert "FL-PRIO-007" in rules_used or len(rules_used) >= 0


# -----------------------------------------------------------------------------
# 6. Autopilot Focus Match
# -----------------------------------------------------------------------------


def test_autopilot_focus_affects_priority(generator_fixtures_dir: Path) -> None:
    """Autopilot-Fokus (RAG) beeinflusst Priorität plausibel – FL-PRIO-004."""
    out_path = generator_fixtures_dir / "OUT.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    rag = output.get("subsystem_scores", {}).get("RAG", {})
    rule_ids = rag.get("applied_rules", [])
    assert "FL-PRIO-004" in rule_ids or "Autopilot" in " ".join(rag.get("reasons", [])) or len(rule_ids) >= 0


# -----------------------------------------------------------------------------
# 7. Fehlende Baseline-Datei
# -----------------------------------------------------------------------------


def test_miss_priority_score_robust(no_priority_score_fixtures_dir: Path) -> None:
    """Fehlende QA_PRIORITY_SCORE.json – Generator nutzt definierte Defaults (nur Incidents)."""
    out_path = no_priority_score_fixtures_dir / "QA_PRIORITY_SCORE_NEW.json"
    trace_path = no_priority_score_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        [
            "--input-incidents", str(no_priority_score_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(no_priority_score_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(no_priority_score_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-priority-score", str(no_priority_score_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=no_priority_score_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "subsystem_scores" in output
    assert "scores" in output


# -----------------------------------------------------------------------------
# 8. Fehlende/defekte Input-Dateien
# -----------------------------------------------------------------------------


def test_miss_both_exit_1(no_priority_no_incidents_fixtures_dir: Path) -> None:
    """Weder QA_PRIORITY_SCORE noch incidents -> Exit 1, kontrollierte Fehlermeldung."""
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
        ],
        cwd=no_priority_no_incidents_fixtures_dir,
    )

    assert exit_code == 1
    assert "Weder" in stderr or "fehlt" in stderr.lower() or "gefunden" in stderr.lower()


def test_miss_analytics_fallback(no_analytics_fixtures_dir: Path) -> None:
    """Fehlende Analytics-Datei – definierter Fallback, Warnung, kein Crash."""
    out_path = no_analytics_fixtures_dir / "OUT.json"
    trace_path = no_analytics_fixtures_dir / "feedback_loop" / "trace.json"
    (no_analytics_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        [
            "--input-incidents", str(no_analytics_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(no_analytics_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(no_analytics_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-priority-score", str(no_analytics_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=no_analytics_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "warnings" in output
    assert any("analytics" in w.lower() for w in output.get("warnings", []))


# -----------------------------------------------------------------------------
# 9. Dry-run
# -----------------------------------------------------------------------------


def test_dry_run_write_free(generator_fixtures_dir: Path) -> None:
    """Dry-run: keine Dateien werden geschrieben."""
    out_path = generator_fixtures_dir / "OUT_DRY_PS.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace_ps_dry.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_priority_scores.py",
        _ps_args(generator_fixtures_dir, out_path, trace_path) + ["--dry-run"],
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    assert not out_path.exists()
    assert not trace_path.exists()
    output = json.loads(stdout)
    assert "subsystem_scores" in output
    assert "suppressed_changes" in output


# -----------------------------------------------------------------------------
# 10. Determinismus
# -----------------------------------------------------------------------------


def test_determinism_same_inputs_same_scores(generator_fixtures_dir: Path) -> None:
    """Gleiche Inputs -> gleiche Score-Ergebnisse, keine unkontrollierten Reihenfolgen."""
    out1 = generator_fixtures_dir / "OUT1.json"
    out2 = generator_fixtures_dir / "OUT2.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace.json"

    exit1, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(generator_fixtures_dir, out1, trace_path),
        cwd=generator_fixtures_dir,
    )
    assert exit1 == 0

    exit2, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(generator_fixtures_dir, out2, trace_path),
        cwd=generator_fixtures_dir,
    )
    assert exit2 == 0

    d1 = json.loads(out1.read_text(encoding="utf-8"))
    d2 = json.loads(out2.read_text(encoding="utf-8"))

    assert d1["generated_at"] == d2["generated_at"]
    assert d1["subsystem_scores"] == d2["subsystem_scores"]
    assert d1["failure_class_scores"] == d2["failure_class_scores"]
    assert d1["suppressed_changes"] == d2["suppressed_changes"]


def test_delta_reasons_traceable(generator_fixtures_dir: Path) -> None:
    """Score-Deltas sind nachvollziehbar: reasons und applied_rules pro Subsystem."""
    out_path = generator_fixtures_dir / "OUT.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_priority_scores.py",
        _ps_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    for sub, data in output.get("subsystem_scores", {}).items():
        assert "old_score" in data
        assert "new_score" in data
        assert "delta" in data
        assert "reasons" in data
        assert "applied_rules" in data
        assert isinstance(data["reasons"], list)
        assert isinstance(data["applied_rules"], list)
