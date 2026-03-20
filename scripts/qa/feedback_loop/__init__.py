"""
QA Feedback Loop – Gemeinsamer technischer Kern.

Projiziert Ergebnisse aus:
- incidents/index.json
- incidents/analytics.json
- QA_AUTOPILOT_V2.json

auf Governance-Artefakte:
- QA_CONTROL_CENTER
- QA_PRIORITY_SCORE
- QA_RISK_RADAR

Der Feedback Loop darf: priorisieren, projizieren, warnen, eskalieren, begründen.
Er darf NICHT: Tests schreiben, Incidents ändern, Regression Catalog, Replay-Daten, Produktcode.
"""

from __future__ import annotations

from .loader import FeedbackLoopInputs, load_feedback_inputs, load_feedback_inputs_from_paths
from .models import (
    FailureClassFeedbackState,
    FeedbackProjectionReport,
    FeedbackRuleResult,
    SubsystemFeedbackState,
    ALL_RULE_IDS,
    FL_PRIO_001,
    FL_PRIO_002,
    FL_PRIO_003,
    FL_PRIO_004,
    FL_PRIO_005,
    FL_PRIO_006,
    FL_PRIO_007,
    FL_RISK_001,
    FL_RISK_002,
    FL_RISK_003,
    FL_RISK_004,
    FL_RISK_005,
    FL_CTRL_001,
    FL_CTRL_002,
    FL_CTRL_003,
    FL_CTRL_004,
    FL_CTRL_005,
)
from .normalizer import normalize_to_failure_class_states, normalize_to_subsystem_states
from .projections import run_feedback_projections
from .rules import (
    apply_control_center_rules,
    apply_priority_rules,
    apply_risk_rules,
)
from .thresholds import (
    INCIDENT_COUNT_ESCALATION,
    INCIDENT_COUNT_PRESSURE,
    REPLAY_GAP_CRITICAL,
    REPLAY_GAP_WARNING,
    REGRESSION_GAP_CRITICAL,
    REGRESSION_GAP_WARNING,
)
from .traces import report_to_dict, trace_report
from .utils import get_project_root, load_json

__all__ = [
    "load_feedback_inputs",
    "load_feedback_inputs_from_paths",
    "FeedbackLoopInputs",
    "SubsystemFeedbackState",
    "FailureClassFeedbackState",
    "FeedbackRuleResult",
    "FeedbackProjectionReport",
    "run_feedback_projections",
    "normalize_to_subsystem_states",
    "normalize_to_failure_class_states",
    "apply_priority_rules",
    "apply_risk_rules",
    "apply_control_center_rules",
    "trace_report",
    "report_to_dict",
    "load_json",
    "get_project_root",
    "ALL_RULE_IDS",
    "FL_PRIO_001",
    "FL_PRIO_002",
    "FL_PRIO_003",
    "FL_PRIO_004",
    "FL_PRIO_005",
    "FL_PRIO_006",
    "FL_PRIO_007",
    "FL_RISK_001",
    "FL_RISK_002",
    "FL_RISK_003",
    "FL_RISK_004",
    "FL_RISK_005",
    "FL_CTRL_001",
    "FL_CTRL_002",
    "FL_CTRL_003",
    "FL_CTRL_004",
    "FL_CTRL_005",
    "INCIDENT_COUNT_ESCALATION",
    "INCIDENT_COUNT_PRESSURE",
    "REPLAY_GAP_CRITICAL",
    "REPLAY_GAP_WARNING",
    "REGRESSION_GAP_CRITICAL",
    "REGRESSION_GAP_WARNING",
]
