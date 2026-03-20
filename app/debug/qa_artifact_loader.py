"""
QA Artifact Loader – Liest docs/qa/artifacts/json/*.json.

Keine QA-Logik, nur Lese-Utility. Graceful handling fehlender Dateien.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _project_root() -> Path:
    # app/debug/qa_artifact_loader.py -> parent=debug, parent.parent=app, parent.parent.parent=project
    return Path(__file__).resolve().parent.parent.parent


def _artifacts_dir() -> Path:
    return _project_root() / "docs" / "qa" / "artifacts" / "json"


def _incidents_path() -> Path:
    return _project_root() / "docs" / "qa" / "incidents" / "index.json"


def load_json(path: Path) -> dict[str, Any] | None:
    """Lädt JSON-Datei. Gibt None bei Fehler oder fehlender Datei."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


@dataclass
class TestInventoryData:
    total_count: int = 0
    domains: dict[str, int] = field(default_factory=dict)


@dataclass
class CoverageData:
    failure_classes_covered: int = 0
    failure_classes_total: int = 0
    missing_coverage: list[str] = field(default_factory=list)


@dataclass
class RiskRadarData:
    subsystems: dict[str, str] = field(default_factory=dict)


@dataclass
class GapStatusData:
    uncovered_failure_classes: list[str] = field(default_factory=list)
    replay_unbound_count: int = 0
    regression_requirement_unbound_count: int = 0
    gap_ids: list[str] = field(default_factory=list)


@dataclass
class IncidentsData:
    open_count: int = 0
    replay_defined: int = 0
    replay_verified: int = 0
    bound_to_regression: int = 0


@dataclass
class StabilityData:
    index: int = 0
    klasse: str = ""
    anomaly_summary: list[str] = field(default_factory=list)


def load_test_inventory() -> TestInventoryData:
    data = TestInventoryData()
    j = load_json(_artifacts_dir() / "QA_TEST_INVENTORY.json")
    if not j:
        return data
    data.total_count = j.get("test_count", 0) or (j.get("summary", {}) or {}).get("test_count", 0)
    data.domains = (j.get("summary", {}) or {}).get("by_test_domain", {})
    return data


def load_coverage() -> CoverageData:
    data = CoverageData()
    j = load_json(_artifacts_dir() / "QA_COVERAGE_MAP.json")
    gap_j = load_json(_artifacts_dir() / "PHASE3_GAP_REPORT.json")
    if j:
        by_axis = j.get("coverage_by_axis", {}) or {}
        fc = by_axis.get("failure_class", {})
        if isinstance(fc, dict):
            covered = sum(1 for v in fc.values() if isinstance(v, dict) and v.get("coverage_strength") == "covered")
            total = len([k for k, v in fc.items() if isinstance(v, dict) and "coverage_strength" in (v or {})])
            data.failure_classes_covered = covered
            data.failure_classes_total = total
    if gap_j:
        for g in gap_j.get("prioritized_gaps", []) or []:
            if g.get("gap_type") == "failure_class_uncovered":
                data.missing_coverage.append(g.get("value", g.get("gap_id", "?")))
    return data


def load_risk_radar() -> RiskRadarData:
    data = RiskRadarData()
    j = load_json(_artifacts_dir() / "QA_RISK_RADAR.json")
    if not j:
        return data
    subs = j.get("subsystems", {}) or {}
    data.subsystems = {k: v.get("new_risk_level", "?") for k, v in subs.items() if isinstance(v, dict)}
    return data


def load_gap_status() -> GapStatusData:
    data = GapStatusData()
    j = load_json(_artifacts_dir() / "PHASE3_GAP_REPORT.json")
    if not j:
        return data
    gap_types = (j.get("gap_type_counts") or {})
    data.replay_unbound_count = gap_types.get("replay_unbound", 0)
    data.regression_requirement_unbound_count = gap_types.get("regression_requirement_unbound", 0)
    for g in j.get("prioritized_gaps", []) or []:
        data.gap_ids.append(g.get("gap_id", g.get("value", "?")))
        if g.get("gap_type") == "failure_class_uncovered":
            data.uncovered_failure_classes.append(g.get("value", g.get("gap_id", "?")))
    return data


def load_incidents() -> IncidentsData:
    data = IncidentsData()
    j = load_json(_incidents_path())
    if not j:
        return data
    m = j.get("metrics", {}) or {}
    data.open_count = m.get("open_incidents", 0)
    data.replay_defined = m.get("replay_defined", 0)
    data.replay_verified = m.get("replay_verified", 0)
    data.bound_to_regression = m.get("bound_to_regression", 0)
    return data


def load_stability() -> StabilityData:
    data = StabilityData()
    stab = load_json(_artifacts_dir() / "QA_STABILITY_INDEX.json")
    anom = load_json(_artifacts_dir() / "QA_ANOMALY_DETECTION.json")
    if stab:
        data.index = stab.get("index", 0)
        data.klasse = stab.get("stabilitaetsklasse", "")
    if anom:
        for w in anom.get("warnsignale", []) or []:
            text = w.get("text", str(w)) if isinstance(w, dict) else str(w)
            data.anomaly_summary.append(text)
    return data
