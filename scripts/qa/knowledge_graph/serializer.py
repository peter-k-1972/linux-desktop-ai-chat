"""
QA Knowledge Graph – Serialisierung.

Konvertiert den Graph zu JSON für QA_KNOWLEDGE_GRAPH.json und Trace.
"""

from __future__ import annotations

from typing import Any

from .models import GraphEdge, GraphNode, KnowledgeGraphOutput


def _node_to_dict(n: GraphNode) -> dict[str, Any]:
    """Konvertiert GraphNode zu Dict."""
    return {
        "id": n.id,
        "node_type": n.node_type,
        "attributes": dict(n.attributes) if n.attributes else {},
    }


def _edge_to_dict(e: GraphEdge) -> dict[str, Any]:
    """Konvertiert GraphEdge zu Dict."""
    return {
        "source_id": e.source_id,
        "target_id": e.target_id,
        "edge_type": e.edge_type,
        "attributes": dict(e.attributes) if e.attributes else {},
    }


def output_to_dict(output: KnowledgeGraphOutput) -> dict[str, Any]:
    """Konvertiert KnowledgeGraphOutput zu JSON-serialisierbarem Dict."""
    return {
        "edges": [_edge_to_dict(e) for e in output.edges],
        "generated_at": output.generated_at,
        "input_sources": output.input_sources,
        "nodes": [_node_to_dict(n) for n in output.nodes],
        "schema_version": output.schema_version,
        "supporting_evidence": output.supporting_evidence,
    }


def build_knowledge_graph_trace(output: KnowledgeGraphOutput) -> dict[str, Any]:
    """Baut Trace-Dict für knowledge_graph_trace.json."""
    return {
        "generated_at": output.generated_at,
        "generator": "knowledge_graph",
        "input_sources": output.input_sources,
        "summary": {
            "node_count": len(output.nodes),
            "edge_count": len(output.edges),
            **output.supporting_evidence,
        },
    }
