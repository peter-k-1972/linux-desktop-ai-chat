"""Domänenmodelle für Workflow-Schedules (keine Qt-Abhängigkeit)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ScheduleTriggerType(str, Enum):
    """Auslöseart für ``schedule_run_log``."""

    DUE = "due"
    MANUAL = "manual"


@dataclass
class WorkflowSchedule:
    schedule_id: str
    workflow_id: str
    enabled: bool
    initial_input_json: str
    next_run_at: str
    last_fired_at: Optional[str]
    created_at: str
    updated_at: str
    rule_json: str
    claim_until: Optional[str] = None


@dataclass
class ScheduleRunLogEntry:
    id: int
    schedule_id: str
    run_id: str
    due_at: str
    claimed_at: str
    trigger_type: ScheduleTriggerType
    finished_status: Optional[str] = None


@dataclass
class ScheduleListRow:
    """Read-Modell für GUI-Listen (optionaler Workflow-Name)."""

    schedule: WorkflowSchedule
    workflow_name: str
