"""
QA Test Strategy Engine – Datenmodelle.

Definiert Output-Struktur: test_domains, guard_requirements, regression_requirements, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# =============================================================================
# Pilotkonstellationen (explizit berücksichtigt)
# =============================================================================

PILOT_1 = {
    "id": 1,
    "name": "Startup / Ollama unreachable",
    "subsystems": {"Startup/Bootstrap", "Provider/Ollama"},
    "guard_type": "startup_degradation_guard",
}

PILOT_2 = {
    "id": 2,
    "name": "RAG / ChromaDB network failure",
    "subsystems": {"RAG"},
    "guard_type": "failure_replay_guard",
}

PILOT_3 = {
    "id": 3,
    "name": "Debug/EventBus / EventType drift",
    "subsystems": {"Debug/EventBus"},
    "guard_type": "event_contract_guard",
}

PILOT_CONSTELLATIONS = (PILOT_1, PILOT_2, PILOT_3)


# =============================================================================
# Output-Strukturen
# =============================================================================


@dataclass(frozen=True)
class TestDomain:
    """Priorisierte Test-Domain."""
    domain: str
    priority: int  # 1 = höchste Priorität
    recommendation_count: int
    subsystems: tuple[str, ...]
    failure_classes: tuple[str, ...]


@dataclass(frozen=True)
class GuardRequirement:
    """Guard-Anforderung aus Guard-Gap-Findings."""
    id: str
    subsystem: str
    guard_type: str
    failure_class: str
    priority: str
    pilot_id: int | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RegressionRequirement:
    """Regression-Anforderung aus Translation-Gaps (incident_not_bound_to_regression)."""
    id: str
    incident_id: str
    subsystem: str
    failure_class: str
    priority: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RecommendedFocusDomain:
    """Empfohlener Fokus-Bereich (Domain + Subsystem)."""
    domain: str
    subsystem: str
    failure_class: str
    priority: str
    pilot_related: bool


@dataclass(frozen=False)
class TestStrategyOutput:
    """Vollständige QA Test Strategy Ausgabe."""
    schema_version: str
    generated_at: str
    input_sources: list[str]
    test_domains: list[TestDomain]
    guard_requirements: list[GuardRequirement]
    regression_requirements: list[RegressionRequirement]
    recommended_focus_domains: list[RecommendedFocusDomain]
    warnings: list[str]
    escalations: list[str]
    supporting_evidence: dict[str, Any]
