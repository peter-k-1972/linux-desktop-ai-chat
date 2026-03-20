"""
Chaos QA: Robustness Tests für den QA Feedback Loop.

Stress-tests mit malformed inputs.
Ziel: Scripts crashen nicht, produzieren Warnings, nutzen Fallbacks.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import (
    ACCEPTANCE_TIMESTAMP,
    _copy_static_fixtures,
    run_generator_script,
)


def _base_args(base: Path) -> dict[str, str]:
    """Standard-Pfade für alle drei Generatoren."""
    inc = base / "incidents"
    return {
        "incidents": str(inc / "index.json"),
        "analytics": str(inc / "analytics.json"),
        "autopilot": str(base / "QA_AUTOPILOT_V2.json"),
        "control_center": str(base / "QA_CONTROL_CENTER.json"),
        "priority_score": str(base / "QA_PRIORITY_SCORE.json"),
        "risk_radar": str(base / "QA_RISK_RADAR.md"),
        "output": str(base / "out.json"),
        "trace": str(base / "feedback_loop" / "trace.json"),
    }


def _run_all_three(base: Path, extra_incidents: Path | None = None) -> tuple[int, int, int]:
    """Führt alle drei Update-Skripte aus. Gibt (cc_exit, ps_exit, rr_exit) zurück."""
    paths = _base_args(base)
    inc = extra_incidents or base / "incidents" / "index.json"
    (base / "feedback_loop").mkdir(parents=True, exist_ok=True)

    cc_args = [
        "--input-incidents", str(inc),
        "--input-analytics", paths["analytics"],
        "--input-autopilot", paths["autopilot"],
        "--input-control-center", paths["control_center"],
        "--input-priority-score", paths["priority_score"],
        "--output", paths["output"].replace("out.json", "cc_out.json"),
        "--trace-output", paths["trace"].replace("trace.json", "cc_trace.json"),
        "--timestamp", ACCEPTANCE_TIMESTAMP,
    ]
    ps_args = [
        "--input-incidents", str(inc),
        "--input-analytics", paths["analytics"],
        "--input-autopilot", paths["autopilot"],
        "--input-priority-score", paths["priority_score"],
        "--output", paths["output"].replace("out.json", "ps_out.json"),
        "--trace-output", paths["trace"].replace("trace.json", "ps_trace.json"),
        "--timestamp", ACCEPTANCE_TIMESTAMP,
    ]
    rr_args = [
        "--input-incidents", str(inc),
        "--input-analytics", paths["analytics"],
        "--input-autopilot", paths["autopilot"],
        "--input-risk-radar", paths["risk_radar"],
        "--input-priority-score", paths["priority_score"],
        "--output", paths["output"].replace("out.json", "rr_out.json"),
        "--trace-output", paths["trace"].replace("trace.json", "rr_trace.json"),
        "--timestamp", ACCEPTANCE_TIMESTAMP,
    ]

    ec_cc, _, _ = run_generator_script("update_control_center.py", cc_args, cwd=base)
    ec_ps, _, _ = run_generator_script("update_priority_scores.py", ps_args, cwd=base)
    ec_rr, _, _ = run_generator_script("update_risk_radar.py", rr_args, cwd=base)
    return ec_cc, ec_ps, ec_rr


# -----------------------------------------------------------------------------
# 1. Invalid JSON
# -----------------------------------------------------------------------------


def test_invalid_json_no_crash(tmp_path: Path) -> None:
    """Invalid JSON: Scripts crashen nicht; Warnings oder Fallback."""
    base = _copy_static_fixtures(tmp_path)
    (base / "incidents" / "index.json").write_text("{invalid json}", encoding="utf-8")

    ec_cc, ec_ps, ec_rr = _run_all_three(base)

    assert ec_cc == 0
    assert ec_ps == 0
    assert ec_rr == 0

    cc = json.loads((base / "cc_out.json").read_text(encoding="utf-8"))
    assert "current_focus" in cc
    assert "global_warnings" in cc or "warnings" in cc
    assert any("incident" in w.lower() for w in (cc.get("global_warnings") or cc.get("warnings") or []))

    ps = json.loads((base / "ps_out.json").read_text(encoding="utf-8"))
    assert "warnings" in ps
    assert any("incident" in w.lower() or "analytics" in w.lower() for w in ps.get("warnings", []))


# -----------------------------------------------------------------------------
# 2. Missing incidents
# -----------------------------------------------------------------------------


def test_missing_incidents_no_crash(tmp_path: Path) -> None:
    """Missing incidents: Datei fehlt; Fallback auf leere Liste."""
    base = _copy_static_fixtures(tmp_path)
    (base / "incidents" / "index.json").unlink(missing_ok=True)
    # CC und RR brauchen Autopilot; PS braucht incidents ODER priority_score
    # Mit priority_score kann PS laufen
    assert (base / "QA_PRIORITY_SCORE.json").exists()

    ec_cc, ec_ps, ec_rr = _run_all_three(base, base / "incidents" / "index.json")

    assert ec_cc == 0
    assert ec_ps == 0
    assert ec_rr == 0

    cc = json.loads((base / "cc_out.json").read_text(encoding="utf-8"))
    assert "feedback_loop_summary" in cc
    assert "global_warnings" in cc or "warnings" in cc


# -----------------------------------------------------------------------------
# 3. Missing analytics
# -----------------------------------------------------------------------------


def test_missing_analytics_no_crash(tmp_path: Path) -> None:
    """Missing analytics: Fallback replay=0.5, reg=0.0."""
    base = _copy_static_fixtures(tmp_path)
    (base / "incidents" / "analytics.json").unlink(missing_ok=True)

    ec_cc, ec_ps, ec_rr = _run_all_three(base)

    assert ec_cc == 0
    assert ec_ps == 0
    assert ec_rr == 0

    ps = json.loads((base / "ps_out.json").read_text(encoding="utf-8"))
    assert "warnings" in ps
    assert any("analytics" in w.lower() for w in ps.get("warnings", []))


# -----------------------------------------------------------------------------
# 4. Unknown subsystem
# -----------------------------------------------------------------------------


def test_unknown_subsystem_no_crash(tmp_path: Path) -> None:
    """Unknown subsystem: Erscheint in Output; kein Crash."""
    base = _copy_static_fixtures(tmp_path)
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"id": "u1", "subsystem": "UnknownSubsystem", "failure_class": "async_race", "severity": "high"},
        ],
    }
    (base / "incidents" / "index.json").write_text(
        json.dumps(incidents, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    ec_cc, ec_ps, ec_rr = _run_all_three(base)

    assert ec_cc == 0
    assert ec_ps == 0
    assert ec_rr == 0

    ps = json.loads((base / "ps_out.json").read_text(encoding="utf-8"))
    assert "UnknownSubsystem" in ps.get("subsystem_scores", {}) or "subsystem_scores" in ps

    rr = json.loads((base / "rr_out.json").read_text(encoding="utf-8"))
    assert "UnknownSubsystem" in rr.get("subsystems", {})


# -----------------------------------------------------------------------------
# 5. Unknown failure class
# -----------------------------------------------------------------------------


def test_unknown_failure_class_no_crash(tmp_path: Path) -> None:
    """Unknown failure class: Erscheint in failure_class_scores; kein Crash."""
    base = _copy_static_fixtures(tmp_path)
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"id": "f1", "subsystem": "RAG", "failure_class": "unknown_failure_class", "severity": "medium"},
        ],
    }
    (base / "incidents" / "index.json").write_text(
        json.dumps(incidents, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    ec_cc, ec_ps, ec_rr = _run_all_three(base)

    assert ec_cc == 0
    assert ec_ps == 0
    assert ec_rr == 0

    ps = json.loads((base / "ps_out.json").read_text(encoding="utf-8"))
    assert "unknown_failure_class" in ps.get("failure_class_scores", {})

    rr = json.loads((base / "rr_out.json").read_text(encoding="utf-8"))
    assert "unknown_failure_class" in rr.get("failure_classes", {})


# -----------------------------------------------------------------------------
# 6. Empty incident list
# -----------------------------------------------------------------------------


def test_empty_incident_list_no_crash(tmp_path: Path) -> None:
    """Empty incident list: Fallback-Subsysteme; minimaler Output."""
    base = _copy_static_fixtures(tmp_path)
    incidents = {"schema_version": "1.0", "incidents": []}
    (base / "incidents" / "index.json").write_text(
        json.dumps(incidents, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    ec_cc, ec_ps, ec_rr = _run_all_three(base)

    assert ec_cc == 0
    assert ec_ps == 0
    assert ec_rr == 0

    cc = json.loads((base / "cc_out.json").read_text(encoding="utf-8"))
    assert "feedback_loop_summary" in cc
    assert "top_incident_pressure_subsystems" in cc["feedback_loop_summary"]


# -----------------------------------------------------------------------------
# 7. Analytics without qa_coverage
# -----------------------------------------------------------------------------


def test_analytics_without_qa_coverage_no_crash(tmp_path: Path) -> None:
    """Analytics ohne qa_coverage: Fallback replay=0.5, reg=0.0."""
    base = _copy_static_fixtures(tmp_path)
    analytics = {"foo": "bar", "other_key": 123}
    (base / "incidents" / "analytics.json").write_text(
        json.dumps(analytics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    ec_cc, ec_ps, ec_rr = _run_all_three(base)

    assert ec_cc == 0
    assert ec_ps == 0
    assert ec_rr == 0

    cc = json.loads((base / "cc_out.json").read_text(encoding="utf-8"))
    assert "current_focus" in cc
    assert "governance_alerts" in cc


# -----------------------------------------------------------------------------
# 8. Autopilot missing fields
# -----------------------------------------------------------------------------


def test_autopilot_missing_fields_no_crash(tmp_path: Path) -> None:
    """Autopilot mit fehlenden Feldern: Leere Strings als Fallback; CC braucht mindestens ein Objekt."""
    base = _copy_static_fixtures(tmp_path)
    # Minimales Autopilot (CC prüft "if not inputs.autopilot_v2" – leeres {} würde Exit 1)
    autopilot = {"recommended_focus_subsystem": "RAG"}
    (base / "QA_AUTOPILOT_V2.json").write_text(
        json.dumps(autopilot, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    ec_cc, ec_ps, ec_rr = _run_all_three(base)

    assert ec_cc == 0
    assert ec_ps == 0
    assert ec_rr == 0

    cc = json.loads((base / "cc_out.json").read_text(encoding="utf-8"))
    assert "current_focus" in cc
    cf = cc["current_focus"]
    assert "recommended_focus_subsystem" in cf
    # Fehlende Felder werden als leer geliefert
    assert cf.get("recommended_focus_subsystem") == "RAG"
