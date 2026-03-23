"""Datentypen für Audit und Incidents (R1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


class AuditEventType:
    """Feste Audit-Event-Codes (V1). Append-only; Werte stabil halten."""

    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_RERUN_STARTED = "workflow_rerun_started"
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    INCIDENT_CREATED = "incident_created"
    INCIDENT_STATUS_CHANGED = "incident_status_changed"
    # R4 Deployment / Distribution (Operations light)
    DEPLOYMENT_TARGET_MUTATED = "deployment_target_mutated"
    DEPLOYMENT_RELEASE_MUTATED = "deployment_release_mutated"
    DEPLOYMENT_ROLLOUT_RECORDED = "deployment_rollout_recorded"


class IncidentStatus:
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class IncidentSeverity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class AuditEventRecord:
    id: Optional[int]
    occurred_at: str
    event_type: str
    actor: Optional[str]
    summary: str
    payload_json: Optional[str]
    project_id: Optional[int]
    workflow_id: Optional[str]
    run_id: Optional[str]
    incident_id: Optional[int]


@dataclass
class IncidentRecord:
    id: Optional[int]
    status: str
    severity: str
    title: str
    short_description: str
    workflow_run_id: str
    workflow_id: str
    project_id: Optional[int]
    first_seen_at: str
    last_seen_at: str
    occurrence_count: int
    fingerprint: str
    diagnostic_code: Optional[str]
    resolution_note: Optional[str]
    created_at: str
    updated_at: str
