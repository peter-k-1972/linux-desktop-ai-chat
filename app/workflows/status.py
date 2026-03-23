"""Status-Enums für Workflow-Definitionen und Ausführung."""

from enum import Enum


class WorkflowDefinitionStatus(str, Enum):
    """Persistierter Validierungs-/Lebenszyklusstatus der Definition."""

    DRAFT = "draft"
    VALID = "valid"
    INVALID = "invalid"


class WorkflowRunStatus(str, Enum):
    """Status eines Workflow-Runs."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeRunStatus(str, Enum):
    """Status eines einzelnen Node-Runs."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
