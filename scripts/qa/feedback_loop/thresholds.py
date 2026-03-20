"""
QA Feedback Loop – Schwellenwerte.

Deterministische Schwellen für Regeln, Eskalationen und Priorisierungen.
"""

from __future__ import annotations

# Incident-basiert
INCIDENT_COUNT_ESCALATION = 3
INCIDENT_COUNT_PRESSURE = 2
INCIDENT_COUNT_CLUSTER = 2

# Replay / Regression
REPLAY_GAP_CRITICAL = 0.2
REPLAY_GAP_WARNING = 0.5
REGRESSION_GAP_CRITICAL = 0.2
REGRESSION_GAP_WARNING = 0.3

# Drift
DRIFT_DENSITY_ESCALATION = 0.5
DRIFT_COUNT_ESCALATION = 2

# Severity-Gewichtung (für weighted_severity)
SEVERITY_WEIGHTS = {
    "blocker": 5.0,
    "critical": 4.0,
    "high": 3.0,
    "medium": 2.0,
    "low": 1.0,
    "cosmetic": 0.5,
}

# Escalation-Level
ESCALATION_NONE = 0
ESCALATION_WARNING = 1
ESCALATION_ELEVATED = 2
ESCALATION_CRITICAL = 3

# Dependency-Weight (Startup-kritische Subsysteme)
DEPENDENCY_WEIGHT_HIGH = 1.2
DEPENDENCY_WEIGHT_MEDIUM = 1.0
DEPENDENCY_WEIGHT_LOW = 0.8
