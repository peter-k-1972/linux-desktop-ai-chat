"""
QA Autopilot v3 – Datenmodelle.

Definiert Finding-Typen und Recommended-Test-Backlog-Struktur.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# Pilotkonstellationen (explizit berücksichtigt)
# =============================================================================

PILOT_1 = {
    "id": 1,
    "name": "Startup / Ollama unreachable",
    "subsystems": {"Startup/Bootstrap", "Provider/Ollama"},
    "failure_classes": {"startup_ordering", "degraded_mode_failure", "optional_dependency_missing"},
    "guard_type": "startup_degradation_guard",
}

PILOT_2 = {
    "id": 2,
    "name": "RAG / ChromaDB network failure",
    "subsystems": {"RAG"},
    "failure_classes": {"rag_silent_failure", "optional_dependency_missing", "degraded_mode_failure", "async_race"},
    "guard_type": "failure_replay_guard",
}

PILOT_3 = {
    "id": 3,
    "name": "Debug/EventBus / EventType drift",
    "subsystems": {"Debug/EventBus"},
    "failure_classes": {"debug_false_truth", "contract_schema_drift"},
    "guard_type": "event_contract_guard",
}

PILOT_CONSTELLATIONS = (PILOT_1, PILOT_2, PILOT_3)

# Drift-Failure-Classes
DRIFT_FAILURE_CLASSES = {"contract_schema_drift", "debug_false_truth", "metrics_false_success"}

# Failure-Class -> Test-Domain
FAILURE_CLASS_TO_TEST_DOMAIN: dict[str, str] = {
    "async_race": "async_behavior",
    "contract_schema_drift": "contracts",
    "debug_false_truth": "contracts",
    "metrics_false_success": "failure_modes",
    "rag_silent_failure": "failure_modes",
    "optional_dependency_missing": "startup",
    "startup_ordering": "startup",
    "degraded_mode_failure": "startup",
    "ui_state_drift": "contracts",
}
DEFAULT_TEST_DOMAIN = "failure_modes"


# =============================================================================
# Finding-Typen
# =============================================================================


@dataclass(frozen=True)
class TestGapFinding:
    """Erkannte Testlücke."""
    id: str
    subsystem: str
    failure_class: str
    gap_type: str  # missing_replay_test, missing_regression_test, missing_contract_test
    reasons: tuple[str, ...]
    incident_count: int
    priority: str  # high, medium, low


@dataclass(frozen=True)
class GuardGapFinding:
    """Erkannte Guard-Lücke."""
    id: str
    subsystem: str
    failure_class: str
    guard_type: str  # failure_replay_guard, event_contract_guard, startup_degradation_guard
    reasons: tuple[str, ...]
    pilot_id: int | None
    priority: str


@dataclass(frozen=True)
class TranslationGapFinding:
    """Erkannte Translation-Gap (Incident nicht an Replay/Regression gebunden)."""
    id: str
    incident_id: str
    subsystem: str
    failure_class: str
    gap_type: str  # incident_not_bound_to_replay, incident_not_bound_to_regression, pilot_not_sufficiently_translated
    reasons: tuple[str, ...]
    priority: str


@dataclass(frozen=True)
class RecommendedTestBacklogItem:
    """Empfohlener Test-Backlog-Eintrag."""
    id: str
    title: str
    subsystem: str
    failure_class: str
    test_domain: str
    test_type: str  # replay, regression, contract
    guard_type: str
    priority: str
    reasons: tuple[str, ...]


@dataclass(frozen=False)
class AutopilotV3Output:
    """Vollständige Autopilot-v3-Ausgabe."""
    schema_version: str
    generated_at: str
    summary: dict[str, Any]
    test_gap_findings: list[TestGapFinding]
    guard_gap_findings: list[GuardGapFinding]
    translation_gap_findings: list[TranslationGapFinding]
    recommended_test_backlog: list[RecommendedTestBacklogItem]
    warnings: list[str]
    escalations: list[str]
    supporting_evidence: dict[str, Any]
    input_sources: list[str] = field(default_factory=list)
