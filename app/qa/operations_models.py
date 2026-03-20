"""
Operations DTOs – Read-Model für Phase-C Operations Center.

Keine Logik, nur Datenstrukturen für operative Arbeitskontexte.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IncidentItem:
    """Ein Incident aus dem Index."""

    incident_id: str
    title: str
    status: str
    severity: str
    subsystem: str
    failure_class: str
    regression_required: bool
    binding_status: str | None
    replay_status: str | None


@dataclass
class IncidentOperationsData:
    """Incident Operations – Übersicht."""

    incident_count: int = 0
    incidents: list[IncidentItem] = field(default_factory=list)
    open_count: int = 0
    bound_count: int = 0
    replay_ready_count: int = 0
    warnings: list[str] = field(default_factory=list)
    has_data: bool = False


@dataclass
class VerificationStatus:
    """QA-Verifikationsstatus."""

    last_run: str = ""
    gaps_closed: bool = True
    orphan_count: int = 0
    verification_steps: list[str] = field(default_factory=list)
    has_data: bool = False


@dataclass
class QAOperationsData:
    """QA Operations – Verifikation, Artefakte."""

    verification: VerificationStatus = field(default_factory=VerificationStatus)
    artifact_links: list[tuple[str, str]] = field(default_factory=list)
    has_data: bool = False


@dataclass
class ReviewBatchItem:
    """Ein Review-Batch (z.B. Orphan-Gruppe)."""

    id: str
    label: str
    count: int
    treat_as: str
    description: str = ""


@dataclass
class ReviewOperationsData:
    """Review Operations – Orphan Backlog, Batches."""

    orphan_count: int = 0
    batches: list[ReviewBatchItem] = field(default_factory=list)
    treat_as: str = ""
    has_data: bool = False


@dataclass
class AuditItem:
    """Ein Audit-Follow-up-Punkt."""

    category: str  # kritisch | mittel | niedrig | empfehlung
    source: str
    description: str
    location: str = ""


@dataclass
class AuditOperationsData:
    """Audit / Technical Debt Operations."""

    items: list[AuditItem] = field(default_factory=list)
    by_category: dict[str, int] = field(default_factory=dict)
    has_data: bool = False


@dataclass
class WorkflowEntry:
    """Ein Guided-Workflow-Einstieg."""

    id: str
    label: str
    description: str
    target: str  # qa_ops | incident_ops | review_ops | audit_ops


@dataclass
class GuidedWorkflowData:
    """Guided Workflow Entry – verfügbare Einstiege."""

    entries: list[WorkflowEntry] = field(default_factory=list)
    has_data: bool = True
