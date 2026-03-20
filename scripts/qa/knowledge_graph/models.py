"""
QA Knowledge Graph – Datenmodelle.

Definiert Nodes und Edges für den Knowledge Graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# Node-Typen
# =============================================================================

NODE_TYPES = ("incident", "failure_class", "guard", "test_domain", "regression_requirement")
EDGE_TYPES = (
    "incident_failure",
    "requires_guard",
    "validated_by",
    "requires_regression",
    "recommended_test",
)


@dataclass(frozen=True)
class GraphNode:
    """Graph-Knoten mit stabiler ID."""
    id: str
    node_type: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphEdge:
    """Graph-Kante mit Typ."""
    source_id: str
    target_id: str
    edge_type: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=False)
class KnowledgeGraphOutput:
    """Vollständige Knowledge-Graph-Ausgabe."""
    schema_version: str
    generated_at: str
    input_sources: list[str]
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    supporting_evidence: dict[str, Any]
