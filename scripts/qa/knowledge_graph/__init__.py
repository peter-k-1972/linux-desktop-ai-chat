"""
QA Knowledge Graph – Beziehungsmodellierung.

Modelliert explizit die Beziehungen zwischen Incidents, Failure Classes,
Guards, Test Domains und Regression Requirements.
Rein analytisch – keine Mutationen anderer Artefakte.
"""

from __future__ import annotations

from .loader import load_knowledge_graph_inputs
from .models import KnowledgeGraphOutput
from .builder import build_knowledge_graph
from .serializer import output_to_dict, build_knowledge_graph_trace

__all__ = [
    "load_knowledge_graph_inputs",
    "build_knowledge_graph",
    "output_to_dict",
    "build_knowledge_graph_trace",
    "KnowledgeGraphOutput",
]
