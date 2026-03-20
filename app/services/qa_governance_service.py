"""
QAGovernanceService – Lese-Service für QA-/Governance-Artefakte.

Lädt Test Inventory, Coverage Map, Incidents, Gaps, Replay-Artefakte.
GUI spricht nur mit diesem Service, nicht direkt mit JSON-Dateien.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_qa_dir() -> Path:
    return _project_root() / "docs" / "qa"


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


@dataclass
class TestEntry:
    """Ein Test aus dem Inventory."""

    id: str
    file_path: str
    test_name: str
    subsystem: str
    test_domain: str
    test_type: str
    component: Optional[str]
    covers_regression: bool
    failure_classes: List[str]
    guard_types: List[str]
    replay_ids: List[str]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoverageEntry:
    """Ein Coverage-Eintrag (Failure Class oder Guard)."""

    key: str
    axis: str
    strength: str
    test_count: int
    test_ids: List[str]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentEntry:
    """Ein Incident."""

    incident_id: str
    title: str
    status: str
    severity: str
    subsystem: str
    failure_class: str
    detected_at: str
    replay_status: Optional[str]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GapEntry:
    """Ein Gap-Eintrag."""

    id: str
    title: str
    gap_type: str
    severity: str
    subsystem: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplayEntry:
    """Ein Replay-Artefakt (aus Incident oder Coverage)."""

    id: str
    incident_id: Optional[str]
    status: str
    raw: Dict[str, Any] = field(default_factory=dict)


class QAGovernanceService:
    """Service für QA-/Governance-Artefakte."""

    def __init__(self, qa_dir: Path | None = None):
        self.qa_dir = Path(qa_dir or _default_qa_dir())

    def list_tests(
        self,
        subsystem_filter: str = "",
        text_filter: str = "",
        limit: int = 500,
    ) -> List[TestEntry]:
        """Listet Tests aus QA_TEST_INVENTORY.json."""
        inv = _load_json(self.qa_dir / "QA_TEST_INVENTORY.json")
        if not inv:
            return []
        tests = inv.get("tests") or []
        result: List[TestEntry] = []
        for t in tests:
            sub = t.get("subsystem") or "unknown"
            if subsystem_filter and sub != subsystem_filter:
                continue
            if text_filter:
                tf = text_filter.lower()
                if tf not in (t.get("test_name") or "").lower() and tf not in (t.get("file_path") or "").lower():
                    continue
            result.append(TestEntry(
                id=t.get("test_id") or t.get("id") or "",
                file_path=t.get("file_path") or "",
                test_name=t.get("test_name") or "",
                subsystem=sub,
                test_domain=t.get("test_domain") or "unknown",
                test_type=t.get("test_type") or "unknown",
                component=t.get("component"),
                covers_regression=bool(t.get("covers_regression")),
                failure_classes=list(t.get("failure_classes") or []),
                guard_types=list(t.get("guard_types") or []),
                replay_ids=list(t.get("replay_ids") or []),
                raw=t,
            ))
            if len(result) >= limit:
                break
        return result

    def get_test_detail(self, test_id: str) -> Optional[TestEntry]:
        """Lädt einen Test nach ID."""
        for t in self.list_tests(limit=10000):
            if t.id == test_id:
                return t
        return None

    def get_test_summary(self) -> Dict[str, Any]:
        """Zusammenfassung aus Test Inventory."""
        inv = _load_json(self.qa_dir / "QA_TEST_INVENTORY.json")
        if not inv:
            return {"test_count": 0, "by_subsystem": {}, "by_test_domain": {}}
        summary = inv.get("summary") or {}
        return {
            "test_count": summary.get("test_count") or inv.get("test_count") or 0,
            "by_subsystem": summary.get("by_subsystem") or {},
            "by_test_domain": summary.get("by_test_domain") or {},
            "by_test_type": summary.get("by_test_type") or {},
        }

    def get_coverage_entries(self, axis: str = "") -> List[CoverageEntry]:
        """Lädt Coverage-Einträge aus QA_COVERAGE_MAP.json."""
        cov = _load_json(self.qa_dir / "QA_COVERAGE_MAP.json")
        if not cov:
            return []
        cov_by = cov.get("coverage_by_axis") or {}
        main_axes = ["failure_class", "guard", "regression_requirement", "replay_binding"]
        axes = [axis] if axis else main_axes
        result: List[CoverageEntry] = []
        for ax in axes:
            data = cov_by.get(ax)
            if not isinstance(data, dict):
                continue
            for key, val in data.items():
                if key in ("covered_count", "total_recommendations", "coverage_strength", "backlog_items"):
                    continue
                if isinstance(val, dict):
                    tc = val.get("test_count", 0)
                    tid = val.get("test_ids") or val.get("covered_by_test_ids") or []
                    strength = val.get("coverage_strength") or "unknown"
                    result.append(CoverageEntry(
                        key=key,
                        axis=ax,
                        strength=strength,
                        test_count=tc,
                        test_ids=tid,
                        raw=val,
                    ))
        return result

    def get_coverage_summary(self) -> Dict[str, Any]:
        """Coverage-Zusammenfassung."""
        cov = _load_json(self.qa_dir / "QA_COVERAGE_MAP.json")
        if not cov:
            return {"summary": {}, "gap_count": {}}
        summary = cov.get("summary") or {}
        return {
            "summary": summary,
            "gap_count": summary.get("gap_count") or {},
            "gap_types": summary.get("gap_types") or {},
            "coverage_strength": summary.get("coverage_strength") or {},
        }

    def list_incidents(self) -> List[IncidentEntry]:
        """Listet Incidents aus docs/qa/incidents/index.json."""
        idx = _load_json(self.qa_dir / "incidents" / "index.json")
        if not idx:
            return []
        incidents = idx.get("incidents") or []
        return [
            IncidentEntry(
                incident_id=i.get("incident_id") or "",
                title=i.get("title") or "",
                status=i.get("status") or "",
                severity=i.get("severity") or "",
                subsystem=i.get("subsystem") or "",
                failure_class=i.get("failure_class") or "",
                detected_at=i.get("detected_at") or "",
                replay_status=i.get("replay_status"),
                raw=i,
            )
            for i in incidents
        ]

    def get_incident_detail(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Lädt Incident-Details (z.B. bindings.json)."""
        bind_path = self.qa_dir / "incidents" / incident_id / "bindings.json"
        return _load_json(bind_path)

    def get_incident_summary(self) -> Dict[str, Any]:
        """Incident-Metriken."""
        idx = _load_json(self.qa_dir / "incidents" / "index.json")
        if not idx:
            return {"incident_count": 0, "metrics": {}, "warnings": []}
        return {
            "incident_count": idx.get("incident_count", 0),
            "metrics": idx.get("metrics") or {},
            "warnings": idx.get("warnings") or [],
            "clusters": idx.get("clusters") or {},
        }

    def list_gaps(self) -> List[GapEntry]:
        """Listet Gaps aus PHASE3_GAP_REPORT.json."""
        report = _load_json(self.qa_dir / "PHASE3_GAP_REPORT.json")
        if not report:
            return []
        prio = report.get("prioritized_gaps") or []
        return [
            GapEntry(
                id=str(g.get("id", "")),
                title=str(g.get("title", "")),
                gap_type=str(g.get("gap_type", "")),
                severity=str(g.get("severity", "")),
                subsystem=str(g.get("subsystem", "")),
                raw=g,
            )
            for g in prio
        ]

    def get_gap_summary(self) -> Dict[str, Any]:
        """Gap-Report-Zusammenfassung."""
        report = _load_json(self.qa_dir / "PHASE3_GAP_REPORT.json")
        if not report:
            return {"orphan_count": 0, "prioritized_count": 0, "gap_type_counts": {}}
        prio = report.get("prioritized_gaps") or []
        return {
            "orphan_count": report.get("orphan_count", 0),
            "prioritized_count": len(prio),
            "gap_type_counts": report.get("gap_type_counts") or {},
            "orphan_breakdown": report.get("orphan_breakdown") or {},
        }

    def list_replays(self) -> List[ReplayEntry]:
        """Listet Replay-Artefakte (aus Incidents + Coverage replay_binding)."""
        result: List[ReplayEntry] = []
        idx = _load_json(self.qa_dir / "incidents" / "index.json")
        if idx:
            for i in idx.get("incidents") or []:
                inc_id = i.get("incident_id") or ""
                replay_status = i.get("replay_status") or "—"
                result.append(ReplayEntry(
                    id=f"Replay-{inc_id}",
                    incident_id=inc_id,
                    status=replay_status,
                    raw=i,
                ))
        cov = _load_json(self.qa_dir / "QA_COVERAGE_MAP.json")
        if cov:
            replay_axis = (cov.get("coverage_by_axis") or {}).get("replay_binding")
            if isinstance(replay_axis, dict):
                bindings = replay_axis.get("bindings") or []
                for b in bindings:
                    inc_id = b.get("incident_id") or ""
                    test_id = b.get("test_id") or ""
                    status = b.get("binding_status") or "unknown"
                    rid = f"Binding-{inc_id}" if inc_id else f"Binding-{test_id[:30]}"
                    result.append(ReplayEntry(
                        id=rid,
                        incident_id=inc_id or None,
                        status=status,
                        raw=b,
                    ))
        return result

    def get_replay_summary(self) -> Dict[str, Any]:
        """Replay-Zusammenfassung."""
        replays = self.list_replays()
        return {
            "count": len(replays),
            "by_status": {},
        }


_qa_service: Optional[QAGovernanceService] = None


def get_qa_governance_service() -> QAGovernanceService:
    """Liefert den globalen QAGovernanceService."""
    global _qa_service
    if _qa_service is None:
        _qa_service = QAGovernanceService()
    return _qa_service
