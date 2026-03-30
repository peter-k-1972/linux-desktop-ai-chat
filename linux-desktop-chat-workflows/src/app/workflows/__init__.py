"""
Workflow-Domain: schlanke Root-Public-Surface fuer Definitionen, Status und Guards.

Split-Vorbereitung:
- ``app.workflows`` re-exportiert bewusst nur die leichtgewichtige Root-Oberfläche.
- Laufzeitnahe Adapter-/Executor-Details bleiben in Untermodulen.
- Dokumentierte Außenkanten liegen derzeit in wenigen Executor-/Registry-Pfaden,
  nicht in der Root-Public-Surface.
"""

from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.registry.node_registry import NodeRegistry, build_default_node_registry
from app.workflows.status import (
    NodeRunStatus,
    WorkflowDefinitionStatus,
    WorkflowRunStatus,
)
from app.workflows.validation.graph_validator import GraphValidator, ValidationResult

__all__ = (
    "WorkflowDefinition",
    "WorkflowNode",
    "WorkflowEdge",
    "WorkflowRun",
    "NodeRun",
    "WorkflowDefinitionStatus",
    "WorkflowRunStatus",
    "NodeRunStatus",
    "GraphValidator",
    "ValidationResult",
    "NodeRegistry",
    "build_default_node_registry",
)
