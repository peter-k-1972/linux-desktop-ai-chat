"""
Drilldown DTOs – Read-Model für Phase-B-Detailansichten.

Keine Logik, nur Datenstrukturen.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GapItem:
    """Ein priorisierter Gap."""

    id: str = ""
    title: str = ""
    severity: str = ""
    score: float = 0.0
    subsystem: str = ""
    gap_type: str = ""


@dataclass
class AxisDetail:
    """Detail pro Coverage-Achse."""

    axis: str
    strength: str
    gap_count: int
    covered_count: int = 0
    total_count: int = 0
    items: list[dict] = field(default_factory=list)


@dataclass
class OrphanBreakdown:
    """Orphan-Backlog-Aufschlüsselung."""

    review_candidates: int = 0
    whitelisted: int = 0
    excluded_by_path: int = 0
    treat_as: str = ""
    ci_blocking: bool = False


@dataclass
class QADrilldownData:
    """QA-Drilldown – alle Detaildaten."""

    gap_items: list[GapItem] = field(default_factory=list)
    coverage_axes: list[AxisDetail] = field(default_factory=list)
    orphan_breakdown: OrphanBreakdown | None = None
    last_verification: str = ""
    has_data: bool = False


@dataclass
class SubsystemDetailData:
    """Subsystem-Detail."""

    name: str
    test_count: int
    status: str
    test_domains: list[tuple[str, int]] = field(default_factory=list)
    failure_classes: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)
    quick_links: list[tuple[str, str]] = field(default_factory=list)
    has_data: bool = False


@dataclass
class GovernanceZone:
    """Eine Governance-/Freeze-Zone."""

    id: str
    label: str
    description: str
    zone_type: str  # stable | active | experimental


@dataclass
class GovernanceData:
    """Governance-Übersicht – Freeze-Zonen."""

    zones: list[GovernanceZone] = field(default_factory=list)
    has_data: bool = False
