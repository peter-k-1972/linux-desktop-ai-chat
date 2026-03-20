"""
QA Knowledge Graph – Graph-Builder.

Führt die Regeln aus und baut den vollständigen Knowledge Graph.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import GraphEdge, GraphNode, KnowledgeGraphOutput
from .rules import (
    collect_failure_class_nodes,
    collect_guard_nodes,
    collect_incident_failure_edges,
    collect_incident_nodes,
    collect_recommended_test_edges,
    collect_regression_requirement_nodes,
    collect_requires_guard_edges,
    collect_requires_regression_edges,
    collect_test_domain_nodes,
    collect_validated_by_edges,
)


def build_knowledge_graph(
    inputs: Any,
    optional_timestamp: str | None = None,
) -> KnowledgeGraphOutput:
    """
    Baut den vollständigen Knowledge Graph aus allen Inputs.
    Deterministisch: sortierte Nodes und Edges.
    """
    generated_at = (
        optional_timestamp
        if optional_timestamp is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    incident_index = inputs.incident_index
    autopilot_v3 = inputs.autopilot_v3
    test_strategy = inputs.test_strategy
    catalog_parsed = inputs.regression_catalog_parsed

    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    # Nodes
    nodes.extend(collect_incident_nodes(incident_index))
    nodes.extend(
        collect_failure_class_nodes(
            incident_index, autopilot_v3, test_strategy, catalog_parsed
        )
    )
    nodes.extend(collect_guard_nodes(autopilot_v3, test_strategy))
    nodes.extend(collect_test_domain_nodes(test_strategy, catalog_parsed))
    nodes.extend(collect_regression_requirement_nodes(test_strategy))

    # Deduplizieren: gleiche IDs nur einmal
    node_by_id: dict[str, GraphNode] = {}
    for n in nodes:
        if n.id not in node_by_id:
            node_by_id[n.id] = n
    nodes = sorted(node_by_id.values(), key=lambda n: n.id)

    # Edges
    edges.extend(collect_incident_failure_edges(incident_index))
    edges.extend(collect_requires_guard_edges(autopilot_v3, test_strategy))
    edges.extend(collect_validated_by_edges(catalog_parsed))
    edges.extend(collect_requires_regression_edges(test_strategy))
    edges.extend(collect_recommended_test_edges(autopilot_v3, test_strategy))

    edges = sorted(edges, key=lambda e: (e.edge_type, e.source_id, e.target_id))

    supporting_evidence: dict[str, Any] = {
        "node_count_by_type": {},
        "edge_count_by_type": {},
        "incident_count": len([n for n in nodes if n.node_type == "incident"]),
        "failure_class_count": len([n for n in nodes if n.node_type == "failure_class"]),
        "guard_count": len([n for n in nodes if n.node_type == "guard"]),
        "test_domain_count": len([n for n in nodes if n.node_type == "test_domain"]),
        "regression_requirement_count": len(
            [n for n in nodes if n.node_type == "regression_requirement"]
        ),
    }
    for n in nodes:
        t = n.node_type
        supporting_evidence["node_count_by_type"][t] = (
            supporting_evidence["node_count_by_type"].get(t, 0) + 1
        )
    for e in edges:
        t = e.edge_type
        supporting_evidence["edge_count_by_type"][t] = (
            supporting_evidence["edge_count_by_type"].get(t, 0) + 1
        )

    return KnowledgeGraphOutput(
        schema_version="1.0",
        generated_at=generated_at,
        input_sources=inputs.loaded_sources,
        nodes=nodes,
        edges=edges,
        supporting_evidence=supporting_evidence,
    )
