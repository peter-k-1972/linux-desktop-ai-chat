"""Laufzeit: WorkflowRun und NodeRun."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.workflows.status import NodeRunStatus, WorkflowRunStatus


def _coerce_workflow_run_status(raw: Any) -> WorkflowRunStatus:
    if isinstance(raw, WorkflowRunStatus):
        return raw
    try:
        return WorkflowRunStatus(str(raw))
    except ValueError:
        return WorkflowRunStatus.PENDING


def _coerce_node_run_status(raw: Any) -> NodeRunStatus:
    if isinstance(raw, NodeRunStatus):
        return raw
    try:
        return NodeRunStatus(str(raw))
    except ValueError:
        return NodeRunStatus.PENDING


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class NodeRun:
    """Ausführungsprotokoll eines einzelnen Knotens."""

    node_run_id: str
    run_id: str
    node_id: str
    node_type: str
    status: NodeRunStatus = NodeRunStatus.PENDING
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    input_payload: Optional[Dict[str, Any]] = None
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_run_id": self.node_run_id,
            "run_id": self.run_id,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "status": self.status.value,
            "started_at": _iso(self.started_at),
            "finished_at": _iso(self.finished_at),
            "input_payload": dict(self.input_payload) if self.input_payload is not None else None,
            "output_payload": dict(self.output_payload) if self.output_payload is not None else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> NodeRun:
        return NodeRun(
            node_run_id=str(data["node_run_id"]),
            run_id=str(data["run_id"]),
            node_id=str(data["node_id"]),
            node_type=str(data["node_type"]),
            status=_coerce_node_run_status(data.get("status", NodeRunStatus.PENDING.value)),
            started_at=_parse_dt(data.get("started_at")),
            finished_at=_parse_dt(data.get("finished_at")),
            input_payload=dict(data["input_payload"]) if data.get("input_payload") is not None else None,
            output_payload=dict(data["output_payload"]) if data.get("output_payload") is not None else None,
            error_message=data.get("error_message"),
            retry_count=int(data.get("retry_count", 0)),
        )


@dataclass
class WorkflowRun:
    """Eine Ausführung eines Workflows."""

    run_id: str
    workflow_id: str
    workflow_version: int
    status: WorkflowRunStatus = WorkflowRunStatus.PENDING
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    initial_input: Dict[str, Any] = field(default_factory=dict)
    final_output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    definition_snapshot: Dict[str, Any] = field(default_factory=dict)
    node_runs: List[NodeRun] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = _utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "workflow_id": self.workflow_id,
            "workflow_version": self.workflow_version,
            "status": self.status.value,
            "created_at": _iso(self.created_at),
            "started_at": _iso(self.started_at),
            "finished_at": _iso(self.finished_at),
            "initial_input": dict(self.initial_input),
            "final_output": dict(self.final_output) if self.final_output is not None else None,
            "error_message": self.error_message,
            "definition_snapshot": dict(self.definition_snapshot),
            "node_runs": [nr.to_dict() for nr in self.node_runs],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> WorkflowRun:
        nrs = data.get("node_runs") or []
        return WorkflowRun(
            run_id=str(data["run_id"]),
            workflow_id=str(data["workflow_id"]),
            workflow_version=int(data["workflow_version"]),
            status=_coerce_workflow_run_status(data.get("status", WorkflowRunStatus.PENDING.value)),
            created_at=_parse_dt(data.get("created_at")),
            started_at=_parse_dt(data.get("started_at")),
            finished_at=_parse_dt(data.get("finished_at")),
            initial_input=dict(data.get("initial_input") or {}),
            final_output=dict(data["final_output"]) if data.get("final_output") is not None else None,
            error_message=data.get("error_message"),
            definition_snapshot=dict(data.get("definition_snapshot") or {}),
            node_runs=[NodeRun.from_dict(x) for x in nrs],
        )


def _iso(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _parse_dt(raw: Any) -> Optional[datetime]:
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw if raw.tzinfo else raw.replace(tzinfo=timezone.utc)
    s = str(raw).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None
