"""
QA Feedback Loop – Datenmodelle.

Definiert SubsystemFeedbackState, FeedbackRuleResult, FeedbackProjectionReport
und zentrale Rule-IDs für die Feedback-Loop-Architektur.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# =============================================================================
# Rule IDs – zentral definiert, wiederverwendbar
# =============================================================================

# Priority
FL_PRIO_001 = "FL-PRIO-001"  # repeated incident pressure increases subsystem priority
FL_PRIO_002 = "FL-PRIO-002"  # replay gap increases subsystem priority
FL_PRIO_003 = "FL-PRIO-003"  # regression gap increases subsystem priority
FL_PRIO_004 = "FL-PRIO-004"  # autopilot focus match increases subsystem priority
FL_PRIO_005 = "FL-PRIO-005"  # dependency sensitivity amplifies subsystem priority delta
FL_PRIO_006 = "FL-PRIO-006"  # rising failure class frequency increases failure class priority
FL_PRIO_007 = "FL-PRIO-007"  # repeated drift pattern increases contract-related priority

# Risk
FL_RISK_001 = "FL-RISK-001"  # incident cluster escalates subsystem risk
FL_RISK_002 = "FL-RISK-002"  # replay gap adds reproducibility risk marker
FL_RISK_003 = "FL-RISK-003"  # regression gap adds regression protection risk marker
FL_RISK_004 = "FL-RISK-004"  # repeated failure cluster elevates risk severity
FL_RISK_005 = "FL-RISK-005"  # repeated drift pattern escalates structural risk

# Control Center
FL_CTRL_001 = "FL-CTRL-001"  # autopilot recommendation updates current focus
FL_CTRL_002 = "FL-CTRL-002"  # replay gap creates governance alert
FL_CTRL_003 = "FL-CTRL-003"  # regression gap creates governance alert
FL_CTRL_004 = "FL-CTRL-004"  # repeated drift creates escalation
FL_CTRL_005 = "FL-CTRL-005"  # pilot constellation status is updated from incident evidence

# Alle Rule-IDs als Tuple für Iteration
ALL_RULE_IDS = (
    FL_PRIO_001, FL_PRIO_002, FL_PRIO_003, FL_PRIO_004, FL_PRIO_005, FL_PRIO_006, FL_PRIO_007,
    FL_RISK_001, FL_RISK_002, FL_RISK_003, FL_RISK_004, FL_RISK_005,
    FL_CTRL_001, FL_CTRL_002, FL_CTRL_003, FL_CTRL_004, FL_CTRL_005,
)


# =============================================================================
# SubsystemFeedbackState
# =============================================================================

@dataclass(frozen=False)
class SubsystemFeedbackState:
    """Zustand eines Subsystems aus Feedback-Signalen."""
    subsystem: str
    incident_count: int = 0
    weighted_severity: float = 0.0
    replay_gap_rate: float = 0.0
    regression_gap_rate: float = 0.0
    drift_density: float = 0.0
    cluster_density: float = 0.0
    autopilot_focus: bool = False
    dependency_weight: float = 0.0
    feedback_pressure_score: float = 0.0
    escalation_level: int = 0


# =============================================================================
# FailureClassFeedbackState (für per_failure_class_results)
# =============================================================================

@dataclass(frozen=False)
class FailureClassFeedbackState:
    """Zustand einer Failure-Class aus Feedback-Signalen."""
    failure_class: str
    incident_count: int = 0
    subsystem_count: int = 0
    weighted_severity: float = 0.0
    replay_gap_rate: float = 0.0
    regression_gap_rate: float = 0.0
    drift_related: bool = False
    feedback_pressure_score: float = 0.0
    escalation_level: int = 0


# =============================================================================
# FeedbackRuleResult
# =============================================================================

@dataclass(frozen=True)
class FeedbackRuleResult:
    """Ergebnis einer angewendeten Feedback-Regel."""
    target_artifact: str
    target_key: str
    old_value: Any
    new_value: Any
    delta: Any
    reasons: tuple[str, ...]
    applied_rule_ids: tuple[str, ...]


# =============================================================================
# FeedbackProjectionReport
# =============================================================================

@dataclass(frozen=False)
class FeedbackProjectionReport:
    """Gesamtbericht der Feedback-Projektion."""
    generated_at: str
    generator: str
    input_sources: list[str]
    global_warnings: list[str]
    per_subsystem_results: dict[str, SubsystemFeedbackState]
    per_failure_class_results: dict[str, FailureClassFeedbackState]
    escalations: list[str]
    suppressed_changes: list[FeedbackRuleResult]
    rule_results: list[FeedbackRuleResult] = field(default_factory=list)
