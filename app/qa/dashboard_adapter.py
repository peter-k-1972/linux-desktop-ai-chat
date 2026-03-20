"""
QA Dashboard Adapter – Read-only Service für die Kommandozentrale.

Liest docs/qa/*.json und docs/qa/PHASE3_GAP_REPORT.json.
Robust gegen fehlende oder partielle Daten.
Keine Abhängigkeit zu scripts/qa.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.qa.drilldown_models import (
    AxisDetail,
    GapItem,
    GovernanceData,
    GovernanceZone,
    OrphanBreakdown,
    QADrilldownData,
    SubsystemDetailData,
)


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_qa_dir() -> Path:
    return _project_root() / "docs" / "qa"


def _load_json(path: Path) -> dict[str, Any] | None:
    """Lädt JSON-Datei. Gibt None bei Fehler oder fehlender Datei."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


@dataclass
class ExecutiveStatus:
    """Executive Status Cards – Kernkennzahlen."""

    test_count: int = 0
    prioritized_gaps: int = 0
    orphan_backlog: int = 0
    last_verification: str = ""
    qa_health: str = "unknown"  # ok | warning | unknown


@dataclass
class CoverageAxisStatus:
    """Coverage-Status pro Achse."""

    axis: str
    strength: str  # covered | partial | gap
    gap_count: int = 0


@dataclass
class SubsystemInfo:
    """Subsystem-Übersicht."""

    name: str
    test_count: int
    status: str = "ok"  # ok | warning | unknown


@dataclass
class DashboardData:
    """Aggregierte Dashboard-Daten."""

    executive: ExecutiveStatus = field(default_factory=ExecutiveStatus)
    coverage_axes: list[CoverageAxisStatus] = field(default_factory=list)
    subsystems: list[SubsystemInfo] = field(default_factory=list)
    gap_warnings: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    has_data: bool = False


class QADashboardAdapter:
    """
    Read-only Adapter für QA-Artefakte.
    Liefert DashboardData für die Kommandozentrale.
    """

    def __init__(self, qa_dir: Path | None = None):
        self.qa_dir = qa_dir or _default_qa_dir()

    def load(self) -> DashboardData:
        """Lädt alle relevanten Daten. Robust gegen fehlende Dateien."""
        data = DashboardData()

        inventory = _load_json(self.qa_dir / "QA_TEST_INVENTORY.json")
        gap_report = _load_json(self.qa_dir / "PHASE3_GAP_REPORT.json")
        coverage_map = _load_json(self.qa_dir / "QA_COVERAGE_MAP.json")

        if inventory or gap_report or coverage_map:
            data.has_data = True

        # Executive Status
        data.executive = self._build_executive(inventory, gap_report, coverage_map)

        # Coverage Axes
        data.coverage_axes = self._build_coverage_axes(coverage_map)

        # Subsystems
        data.subsystems = self._build_subsystems(inventory)

        # Gap Warnings
        data.gap_warnings = self._build_gap_warnings(gap_report, coverage_map)

        # Next Actions
        data.next_actions = self._build_next_actions(data)

        return data

    def _build_executive(
        self,
        inventory: dict | None,
        gap_report: dict | None,
        coverage_map: dict | None,
    ) -> ExecutiveStatus:
        status = ExecutiveStatus()

        if inventory:
            summary = inventory.get("summary") or {}
            status.test_count = summary.get("test_count") or inventory.get("test_count") or 0

        if gap_report:
            status.prioritized_gaps = len(gap_report.get("prioritized_gaps") or [])
            status.orphan_backlog = gap_report.get("orphan_count", 0)
            status.last_verification = gap_report.get("generated_at", "")

        if coverage_map:
            inv_snap = coverage_map.get("inventory_snapshot") or {}
            if status.test_count == 0:
                status.test_count = inv_snap.get("test_count", 0)
            if not status.last_verification:
                status.last_verification = coverage_map.get("generated_at", "")

        # QA Health: ok wenn keine priorisierten Gaps, warning bei orphan backlog
        if status.prioritized_gaps > 0:
            status.qa_health = "warning"
        elif status.orphan_backlog > 0:
            status.qa_health = "warning"
        elif status.test_count > 0:
            status.qa_health = "ok"
        else:
            status.qa_health = "unknown"

        return status

    def _build_coverage_axes(self, coverage_map: dict | None) -> list[CoverageAxisStatus]:
        axes = ["failure_class", "guard", "regression_requirement", "replay_binding"]
        result: list[CoverageAxisStatus] = []

        if not coverage_map:
            for ax in axes:
                result.append(CoverageAxisStatus(axis=ax, strength="unknown", gap_count=0))
            return result

        summary = coverage_map.get("summary") or {}
        strength_map = summary.get("coverage_strength") or {}
        gap_map = summary.get("gap_count") or {}
        gap_types = summary.get("gap_types") or {}

        axis_to_gap_key = {
            "failure_class": "failure_class_uncovered",
            "guard": "guard_missing",
            "regression_requirement": "regression_requirement_unbound",
            "replay_binding": "replay_unbound",
        }

        for ax in axes:
            strength = strength_map.get(ax, "unknown")
            gap_key = axis_to_gap_key.get(ax, "")
            gap_count = gap_types.get(gap_key, gap_map.get(ax, 0))
            result.append(CoverageAxisStatus(axis=ax, strength=str(strength), gap_count=gap_count))

        return result

    def _build_subsystems(self, inventory: dict | None) -> list[SubsystemInfo]:
        order = [
            "Chat",
            "RAG",
            "Provider/Ollama",
            "Prompt-System",
            "Agentensystem",
            "Debug/EventBus",
            "Tools",
            "Startup/Bootstrap",
            "Metrics",
            "Persistenz/SQLite",
            "unknown",
        ]

        if not inventory:
            return [SubsystemInfo(name=n, test_count=0, status="unknown") for n in order]

        by_subsystem = (inventory.get("summary") or {}).get("by_subsystem") or {}
        result: list[SubsystemInfo] = []

        for name in order:
            count = by_subsystem.get(name, 0)
            status = "ok" if count > 0 else "unknown"
            result.append(SubsystemInfo(name=name, test_count=count, status=status))

        return result

    def _build_gap_warnings(
        self, gap_report: dict | None, coverage_map: dict | None
    ) -> list[str]:
        warnings: list[str] = []

        if gap_report:
            orphan = gap_report.get("orphan_count", 0)
            if orphan > 0:
                warnings.append(f"Orphan Review Backlog: {orphan} Tests zur Prüfung")
            prio = len(gap_report.get("prioritized_gaps") or [])
            if prio > 0:
                warnings.append(f"Priorisierte Gaps: {prio}")

        return warnings

    def _build_next_actions(self, data: DashboardData) -> list[str]:
        actions: list[str] = []

        if data.executive.orphan_backlog > 0:
            actions.append("Orphan Review – Tests im Backlog prüfen")
        if data.executive.prioritized_gaps > 0:
            actions.append("Gap-Follow-up – priorisierte Gaps adressieren")
        if data.executive.test_count == 0 and data.has_data is False:
            actions.append("QA-Artefakte generieren – build_test_inventory ausführen")

        # Auffällige Subsysteme: wenig oder keine Tests
        low_coverage = [s for s in data.subsystems if s.test_count < 5 and s.name != "unknown"]
        if low_coverage:
            names = ", ".join(s.name for s in low_coverage[:3])
            actions.append(f"Subsystem-Cleanup – {names} hat wenige Tests")

        if not actions:
            actions.append("QA-Gesundheit stabil – keine dringenden Aktionen")

        return actions

    # --- Phase B: Drilldown-Loader ---

    def load_qa_drilldown(self) -> QADrilldownData:
        """Lädt QA-Detaildaten für Drilldown."""
        result = QADrilldownData()
        gap_report = _load_json(self.qa_dir / "PHASE3_GAP_REPORT.json")
        coverage_map = _load_json(self.qa_dir / "QA_COVERAGE_MAP.json")

        if gap_report or coverage_map:
            result.has_data = True

        # Priorisierte Gaps
        for g in (gap_report or {}).get("prioritized_gaps") or []:
            result.gap_items.append(GapItem(
                id=str(g.get("id", "")),
                title=str(g.get("title", "")),
                severity=str(g.get("severity", "")),
                score=float(g.get("score", 0)),
                subsystem=str(g.get("subsystem", "")),
                gap_type=str(g.get("gap_type", "")),
            ))

        # Orphan Breakdown (gap_report oder coverage_map.governance)
        ob = (gap_report or {}).get("orphan_breakdown") or ((coverage_map or {}).get("governance") or {}).get("orphan_breakdown") or {}
        result.orphan_breakdown = OrphanBreakdown(
            review_candidates=ob.get("review_candidates", (gap_report or {}).get("orphan_count", 0)),
            whitelisted=ob.get("whitelisted", 0),
            excluded_by_path=ob.get("excluded_by_path", 0),
            treat_as=ob.get("treat_as", ""),
            ci_blocking=ob.get("ci_blocking", False),
        )

        # Coverage-Achsen mit Details
        axes = ["failure_class", "guard", "regression_requirement", "replay_binding"]
        cov_by = (coverage_map or {}).get("coverage_by_axis") or {}
        summary = (coverage_map or {}).get("summary") or {}
        strength_map = summary.get("coverage_strength") or {}
        gap_types = summary.get("gap_types") or {}
        axis_to_gap = {
            "failure_class": "failure_class_uncovered",
            "guard": "guard_missing",
            "regression_requirement": "regression_requirement_unbound",
            "replay_binding": "replay_unbound",
        }

        for ax in axes:
            axis_data = cov_by.get(ax)
            strength = strength_map.get(ax, "unknown")
            gap_key = axis_to_gap.get(ax, "")
            gap_count = gap_types.get(gap_key, 0)
            covered = 0
            total = 0
            items: list[dict] = []

            if isinstance(axis_data, dict):
                if "covered_count" in axis_data and "total_recommendations" in axis_data:
                    covered = axis_data.get("covered_count", 0)
                    total = axis_data.get("total_recommendations", 0)
                elif "covered_count" in axis_data and "required_count" in axis_data:
                    covered = axis_data.get("covered_count", 0)
                    total = axis_data.get("required_count", 0)
                elif "bound_count" in axis_data and "total_replays" in axis_data:
                    covered = axis_data.get("bound_count", 0)
                    total = axis_data.get("total_replays", 0)
                else:
                    for k, v in axis_data.items():
                        if isinstance(v, dict) and ("test_count" in v or "test_ids" in v):
                            covered += 1
                            total += 1
                            items.append({
                                "key": k,
                                "strength": str(v.get("coverage_strength", "")),
                                "test_count": v.get("test_count", 0),
                            })

            result.coverage_axes.append(AxisDetail(
                axis=ax,
                strength=str(strength),
                gap_count=gap_count,
                covered_count=covered,
                total_count=total,
                items=items,
            ))

        result.last_verification = (
            (gap_report or {}).get("generated_at")
            or (coverage_map or {}).get("generated_at")
            or ""
        )
        return result

    def load_subsystem_detail(self, subsystem_name: str) -> SubsystemDetailData:
        """Lädt Detaildaten für ein Subsystem."""
        inventory = _load_json(self.qa_dir / "QA_TEST_INVENTORY.json")
        coverage_map = _load_json(self.qa_dir / "QA_COVERAGE_MAP.json")

        result = SubsystemDetailData(
            name=subsystem_name,
            test_count=0,
            status="unknown",
            has_data=bool(inventory or coverage_map),
        )

        if inventory:
            by_sub = (inventory.get("summary") or {}).get("by_subsystem") or {}
            result.test_count = by_sub.get(subsystem_name, 0)
            result.status = "ok" if result.test_count > 0 else "unknown"

            # Test-Domains für dieses Subsystem
            tests = inventory.get("tests") or []
            domain_counts: dict[str, int] = {}
            failure_set: set[str] = set()
            for t in tests:
                if t.get("subsystem") != subsystem_name:
                    continue
                dom = t.get("test_domain") or "unknown"
                domain_counts[dom] = domain_counts.get(dom, 0) + 1
                for fc in t.get("failure_classes") or []:
                    failure_set.add(fc)
            result.test_domains = sorted(domain_counts.items(), key=lambda x: -x[1])
            result.failure_classes = sorted(failure_set)

        # Hints / Quick Links
        result.hints = []
        result.quick_links = [
            ("Gap Report", "PHASE3_GAP_REPORT.md"),
            ("Coverage Map", "QA_COVERAGE_MAP.json"),
            ("Test Inventory", "QA_TEST_INVENTORY.json"),
        ]
        if result.test_count == 0 and subsystem_name != "unknown":
            result.hints.append("Keine Tests diesem Subsystem zugeordnet.")
        return result

    def load_governance(self) -> GovernanceData:
        """Lädt Governance-/Freeze-Zonen-Übersicht."""
        result = GovernanceData()
        result.zones = [
            GovernanceZone(
                id="qa_core",
                label="Stabiler QA-Kern",
                description="Coverage Map, Gap Report, Orphan-Governance – Phase 3 verifiziert.",
                zone_type="stable",
            ),
            GovernanceZone(
                id="product",
                label="Aktive Produktentwicklung",
                description="Chat, RAG, Agenten, Provider, Prompts – laufende Feature-Entwicklung.",
                zone_type="active",
            ),
            GovernanceZone(
                id="experimental",
                label="Experimentelle Bereiche",
                description="Neue Tools, Research-Agenten, optionale Integrationen.",
                zone_type="experimental",
            ),
        ]
        result.has_data = True
        return result
