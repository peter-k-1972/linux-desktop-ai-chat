"""Pipeline- und Step-Status."""

from enum import Enum


class PipelineStatus(str, Enum):
    """Gesamtstatus eines Pipeline-Runs."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Status eines einzelnen Pipeline-Schritts."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
