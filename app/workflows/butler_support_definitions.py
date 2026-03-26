"""Minimale Workflow-Definitionen für den Project Butler (Phase 1)."""

from __future__ import annotations

from typing import List

from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode

WORKFLOW_ID_ANALYZE_DECIDE_DOCUMENT = "workflow.analyze_decide_document"
WORKFLOW_ID_CONTEXT_INSPECT = "workflow.context_inspect"

_PY = "python_callable"


def _tc_py(callable_path: str, *, merge: bool = True) -> dict:
    return {
        "executor_type": _PY,
        "merge_step_output_into_payload": merge,
        "executor_config": {"callable": callable_path},
    }


def _edges_linear(node_ids: List[str]) -> List[WorkflowEdge]:
    return [WorkflowEdge(f"e_{a}__{b}", a, b) for a, b in zip(node_ids, node_ids[1:])]


def build_analyze_decide_document_workflow_definition() -> WorkflowDefinition:
    nodes: List[WorkflowNode] = [
        WorkflowNode("s", "start", title="Start"),
        WorkflowNode(
            "run",
            "tool_call",
            title="Analyse / Entscheid / Doku (Phase 1)",
            config=_tc_py("app.workflows.butler_support_tools.butler_analyze_decide_document_phase1"),
        ),
        WorkflowNode("e", "end", title="Ende"),
    ]
    order = [n.node_id for n in nodes]
    return WorkflowDefinition(
        workflow_id=WORKFLOW_ID_ANALYZE_DECIDE_DOCUMENT,
        name="Analyze → Decide → Document (Butler Phase 1)",
        description="Einfacher deterministischer Pfad; später erweiterbar um Agenten.",
        nodes=nodes,
        edges=_edges_linear(order),
    )


def build_context_inspect_workflow_definition() -> WorkflowDefinition:
    nodes: List[WorkflowNode] = [
        WorkflowNode("s", "start", title="Start"),
        WorkflowNode(
            "run",
            "tool_call",
            title="Kontext-Inspect (Phase 1)",
            config=_tc_py("app.workflows.butler_support_tools.butler_context_inspect_phase1"),
        ),
        WorkflowNode("e", "end", title="Ende"),
    ]
    order = [n.node_id for n in nodes]
    return WorkflowDefinition(
        workflow_id=WORKFLOW_ID_CONTEXT_INSPECT,
        name="Context Inspect (Butler Phase 1)",
        description="Einfacher deterministischer Pfad; später z. B. ContextInspectionService.",
        nodes=nodes,
        edges=_edges_linear(order),
    )


def all_butler_support_definitions() -> List[WorkflowDefinition]:
    """Alle nicht-dev_assist Butler-Workflows (zum Registrieren in der DB)."""
    return [
        build_analyze_decide_document_workflow_definition(),
        build_context_inspect_workflow_definition(),
    ]
