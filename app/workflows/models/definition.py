"""Workflow-Definition: Knoten, Kanten, Metadaten."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.workflows.status import WorkflowDefinitionStatus


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class WorkflowNode:
    """Ein Knoten im Workflow-Graphen."""

    node_id: str
    node_type: str
    title: str = ""
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    position: Optional[Dict[str, float]] = None
    is_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "title": self.title,
            "description": self.description,
            "config": dict(self.config),
            "is_enabled": self.is_enabled,
        }
        if self.position is not None:
            d["position"] = dict(self.position)
        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> WorkflowNode:
        pos = data.get("position")
        return WorkflowNode(
            node_id=str(data["node_id"]),
            node_type=str(data["node_type"]),
            title=str(data.get("title") or ""),
            description=str(data.get("description") or ""),
            config=dict(data.get("config") or {}),
            position=dict(pos) if isinstance(pos, dict) else None,
            is_enabled=bool(data.get("is_enabled", True)),
        )


@dataclass
class WorkflowEdge:
    """Kante zwischen zwei Knoten."""

    edge_id: str
    source_node_id: str
    target_node_id: str
    source_port: Optional[str] = None
    target_port: Optional[str] = None
    condition: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
        }
        if self.source_port is not None:
            d["source_port"] = self.source_port
        if self.target_port is not None:
            d["target_port"] = self.target_port
        if self.condition is not None:
            d["condition"] = self.condition
        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> WorkflowEdge:
        return WorkflowEdge(
            edge_id=str(data["edge_id"]),
            source_node_id=str(data["source_node_id"]),
            target_node_id=str(data["target_node_id"]),
            source_port=data.get("source_port"),
            target_port=data.get("target_port"),
            condition=data.get("condition"),
        )


@dataclass
class WorkflowDefinition:
    """Autoritative Workflow-Definition (nicht UI-State).

    project_id None = globaler Workflow; sonst Zuordnung zu app.projects (Persistenz + JSON).
    """

    workflow_id: str
    name: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    description: str = ""
    version: int = 1
    schema_version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowDefinitionStatus = WorkflowDefinitionStatus.DRAFT
    project_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = _utc_now()
        if self.updated_at is None:
            self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "schema_version": self.schema_version,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "metadata": dict(self.metadata),
            "status": self.status.value,
            "project_id": self.project_id,
            "created_at": _dt_iso(self.created_at),
            "updated_at": _dt_iso(self.updated_at),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> WorkflowDefinition:
        st_raw = data.get("status", WorkflowDefinitionStatus.DRAFT.value)
        try:
            st = WorkflowDefinitionStatus(str(st_raw))
        except ValueError:
            st = WorkflowDefinitionStatus.DRAFT
        raw_pid = data.get("project_id")
        project_id: Optional[int] = None
        if raw_pid is not None:
            try:
                project_id = int(raw_pid)
            except (TypeError, ValueError):
                project_id = None
        return WorkflowDefinition(
            workflow_id=str(data["workflow_id"]),
            name=str(data.get("name") or data["workflow_id"]),
            description=str(data.get("description") or ""),
            version=int(data.get("version", 1)),
            schema_version=int(data.get("schema_version", 1)),
            nodes=[WorkflowNode.from_dict(x) for x in (data.get("nodes") or [])],
            edges=[WorkflowEdge.from_dict(x) for x in (data.get("edges") or [])],
            metadata=dict(data.get("metadata") or {}),
            status=st,
            project_id=project_id,
            created_at=_parse_dt(data.get("created_at")),
            updated_at=_parse_dt(data.get("updated_at")),
        )

    def node_by_id(self, node_id: str) -> Optional[WorkflowNode]:
        for n in self.nodes:
            if n.node_id == node_id:
                return n
        return None


def _dt_iso(dt: Optional[datetime]) -> Optional[str]:
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
    s = str(raw)
    s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None
