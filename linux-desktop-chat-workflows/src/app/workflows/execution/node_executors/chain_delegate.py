"""chain_delegate: TaskPlanner + ExecutionEngine über workflow_orchestration_adapter."""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.workflow_orchestration_adapter import run_workflow_orchestration
from app.workflows.execution.context import RunContext
from app.workflows.execution.node_executors.agent import extract_agent_prompt
from app.workflows.execution.node_executors.base import BaseNodeExecutor
from app.workflows.models.definition import WorkflowNode


class ChainDelegateNodeExecutor(BaseNodeExecutor):
    """
    Orchestrierung ohne ChatWidget: Planner erzeugt TaskGraph, Ausführung via
    ``run_workflow_agent`` als run_fn (execute-Modus).
    """

    def execute(
        self,
        node: WorkflowNode,
        input_payload: Optional[Dict[str, Any]],
        context: RunContext,
    ) -> Dict[str, Any]:
        cfg = dict(node.config or {})
        mode = str(cfg.get("mode") or "execute").strip().lower()
        if mode not in ("plan_only", "execute"):
            raise ValueError("chain_delegate: config.mode muss 'plan_only' oder 'execute' sein.")

        prompt = extract_agent_prompt(input_payload)
        mo = cfg.get("model_override")
        if mo is not None:
            mo = str(mo).strip() or None
        pm = cfg.get("planner_model")
        if pm is not None:
            pm = str(pm).strip() or None

        result = run_workflow_orchestration(
            prompt,
            mode=mode,
            model_override=mo,
            planner_model=pm,
        )
        if not isinstance(result, dict):
            raise TypeError("Orchestrierungsadapter muss dict zurückgeben.")
        return {
            "result_text": str(result.get("result_text") or ""),
            "aggregated_output": str(result.get("aggregated_output") or result.get("result_text") or ""),
            "graph_summary": result.get("graph_summary"),
            "delegation_metadata": dict(result.get("delegation_metadata") or {}),
            "subresults": list(result.get("subresults") or []),
        }
