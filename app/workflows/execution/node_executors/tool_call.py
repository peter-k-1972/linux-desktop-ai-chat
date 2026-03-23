"""tool_call: Pipeline StepExecutor-Registry (sync), keine Shell-Erweiterung."""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.pipelines.executors.registry import get_executor_registry
from app.workflows.execution.context import RunContext
from app.workflows.execution.node_executors.base import BaseNodeExecutor
from app.workflows.models.definition import WorkflowNode


class ToolCallNodeExecutor(BaseNodeExecutor):
    """
    Ruft einen registrierten StepExecutor (pipelines) auf.

    config:
      - executor_type: z. B. python_callable, shell, …
      - executor_config: an execute(step_id, config, context) übergebenes Config-Dict
    context für den Executor = zusammengeführte Eingabe (Vorgänger-Output).
    """

    def execute(
        self,
        node: WorkflowNode,
        input_payload: Optional[Dict[str, Any]],
        context: RunContext,
    ) -> Dict[str, Any]:
        cfg = dict(node.config or {})
        et = str(cfg.get("executor_type") or "").strip()
        if not et:
            raise ValueError("tool_call: executor_type erforderlich.")
        exec_cfg = cfg.get("executor_config")
        if exec_cfg is not None and not isinstance(exec_cfg, dict):
            raise ValueError("tool_call: executor_config muss ein Objekt sein.")
        exec_cfg = dict(exec_cfg or {})

        reg = get_executor_registry()
        executor = reg.get(et)
        if executor is None:
            raise ValueError(f"tool_call: unbekannter executor_type {et!r}.")

        ctx = dict(input_payload or {})
        step_id = str(cfg.get("step_id") or node.node_id)
        sr = executor.execute(step_id, exec_cfg, ctx)
        if not sr.success:
            raise RuntimeError(sr.error or "Tool-Ausführung fehlgeschlagen.")

        arts = []
        for a in sr.artifacts or []:
            arts.append(
                {
                    "step_id": getattr(a, "step_id", ""),
                    "key": getattr(a, "key", ""),
                    "value": getattr(a, "value", None),
                    "artifact_type": getattr(a, "artifact_type", "file"),
                }
            )
        return {
            "tool_result": dict(sr.output or {}),
            "logs": list(sr.logs or []),
            "artifacts": arts,
        }
