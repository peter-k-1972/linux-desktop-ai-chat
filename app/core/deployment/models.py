"""R4: Deployment / Distribution — DTOs und Konstanten (kein Qt)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class ReleaseLifecycle:
    DRAFT = "draft"
    READY = "ready"
    ARCHIVED = "archived"


class RolloutOutcome:
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DeploymentTargetRecord:
    target_id: str
    name: str
    kind: Optional[str]
    notes: Optional[str]
    project_id: Optional[int]
    created_at: str
    updated_at: str


@dataclass
class DeploymentReleaseRecord:
    release_id: str
    display_name: str
    version_label: str
    artifact_kind: str
    artifact_ref: str
    lifecycle_status: str
    project_id: Optional[int]
    created_at: str
    updated_at: str


@dataclass
class DeploymentRolloutRecord:
    rollout_id: str
    release_id: str
    target_id: str
    outcome: str
    message: Optional[str]
    started_at: Optional[str]
    finished_at: Optional[str]
    recorded_at: str
    workflow_run_id: Optional[str]
    project_id: Optional[int]


@dataclass
class RolloutListFilter:
    target_id: Optional[str] = None
    release_id: Optional[str] = None
    outcome: Optional[str] = None
    since_iso: Optional[str] = None
    until_iso: Optional[str] = None
    limit: int = 500
