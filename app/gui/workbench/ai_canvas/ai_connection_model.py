"""
Graph edge list backing future visual connections (Comfy/Langflow-style).

Edges reference logical ports so a later renderer can snap curves to anchors.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


def new_edge_id() -> str:
    return uuid.uuid4().hex[:10]


@dataclass(frozen=True, slots=True)
class AiGraphEdge:
    edge_id: str
    source_node_id: str
    source_port: str
    target_node_id: str
    target_port: str


@dataclass(slots=True)
class AiGraphDocument:
    """Authoritative graph state for one AI canvas tab."""

    nodes: dict[str, AiNodeInstance] = field(default_factory=dict)
    edges: list[AiGraphEdge] = field(default_factory=list)
