"""Schlankes Read-Model für Run-Listen ohne NodeRuns (O1)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class WorkflowRunSummary:
    """Aggregate aus workflow_runs ⋈ workflows — keine NodeRun-Daten."""

    run_id: str
    workflow_id: str
    workflow_name: str
    workflow_version: int
    project_id: Optional[int]
    status: str
    created_at: Optional[datetime]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error_message: Optional[str]
