"""
Workflow → TaskPlanner + ExecutionEngine ohne ChatWidget-run_fn.

``execute``-Modus injiziert eine async run_fn, die ``run_workflow_agent`` (Backend)
nutzt — dieselbe Schnittstelle wie der ``agent``-Workflow-Knoten.

``plan_only`` führt keinen ExecutionEngine-Lauf aus (nur TaskGraph aus dem Planner).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from app.agents.execution_engine import ExecutionEngine
from app.agents.task import TaskStatus
from app.agents.task_graph import TaskGraph
from app.agents.task_planner import TaskPlanner

logger = logging.getLogger(__name__)

WorkflowOrchestrationFn = Callable[..., Dict[str, Any]]

_override: Optional[WorkflowOrchestrationFn] = None


def set_workflow_orchestration_override(fn: Optional[WorkflowOrchestrationFn]) -> None:
    """Nur für Tests: synchroner Stub statt asyncio.run(TaskPlanner/ExecutionEngine)."""
    global _override
    _override = fn


def _graph_summary(graph: TaskGraph) -> Dict[str, Any]:
    tasks: List[Dict[str, Any]] = []
    for t in graph.get_all_tasks():
        tasks.append(
            {
                "id": t.id,
                "description": (t.description or "")[:500],
                "assigned_agent": t.assigned_agent,
                "dependencies": list(t.dependencies),
                "tool_hint": t.tool_hint,
                "status": t.status.value,
            }
        )
    return {"tasks": tasks, "task_count": len(tasks)}


def _plan_only_result(graph: TaskGraph) -> Dict[str, Any]:
    summary = _graph_summary(graph)
    lines = [f"{i + 1}. {x['description']}" for i, x in enumerate(summary["tasks"]) if x.get("description")]
    result_text = "\n".join(lines) if lines else "(keine Tasks)"
    return {
        "result_text": result_text,
        "aggregated_output": result_text,
        "graph_summary": summary,
        "delegation_metadata": {"mode": "plan_only"},
        "subresults": [],
    }


async def _run_async(
    prompt: str,
    *,
    mode: str,
    model_override: Optional[str],
    planner_model: Optional[str],
) -> Dict[str, Any]:
    mid = (planner_model or "").strip() or "qwen2.5:latest"
    planner = TaskPlanner(llm_complete_fn=None, model_id=mid)
    graph = await planner.plan(prompt)

    if mode == "plan_only":
        return _plan_only_result(graph)

    if mode != "execute":
        raise ValueError(f"chain_delegate: unbekannter mode {mode!r} (erlaubt: plan_only, execute).")

    from app.services.workflow_agent_adapter import run_workflow_agent

    eng = ExecutionEngine()
    mo = str(model_override).strip() if model_override is not None else None
    if mo == "":
        mo = None

    async def run_fn(agent_id: str, p: str, ctx: Dict[str, Any]) -> str:
        use_mo = mo
        if use_mo is None and isinstance(ctx, dict):
            raw = ctx.get("model_override")
            if raw is not None:
                use_mo = str(raw).strip() or None
        result = await asyncio.to_thread(run_workflow_agent, agent_id or "", p, use_mo)
        if not result.get("success"):
            raise RuntimeError(str(result.get("error") or "Agent-Ausführung fehlgeschlagen."))
        return str(result.get("response_text") or "")

    aggregated = await eng.run_graph(graph, run_fn=run_fn)

    failed = [t for t in graph.get_all_tasks() if t.status == TaskStatus.FAILED]
    if failed:
        msgs = [str(t.error or "Task fehlgeschlagen") for t in failed]
        raise RuntimeError("; ".join(msgs))

    if "Keine Run-Funktion" in aggregated and aggregated.strip().startswith("Fehler:"):
        raise RuntimeError(aggregated)

    summary = _graph_summary(graph)
    return {
        "result_text": aggregated,
        "aggregated_output": aggregated,
        "graph_summary": summary,
        "delegation_metadata": {"mode": "execute"},
        "subresults": [],
    }


def run_workflow_orchestration(
    prompt: str,
    *,
    mode: str = "execute",
    model_override: Optional[str] = None,
    planner_model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Synchroner Einstieg für ``chain_delegate``.

    Raises:
        RuntimeError: bei aktivem Event-Loop (wie workflow_agent_adapter) oder Orchestrationsfehler
    """
    if _override is not None:
        return _override(
            prompt,
            mode=mode,
            model_override=model_override,
            planner_model=planner_model,
        )

    async def _go() -> Dict[str, Any]:
        return await _run_async(
            prompt,
            mode=mode,
            model_override=model_override,
            planner_model=planner_model,
        )

    try:
        return asyncio.run(_go())
    except RuntimeError as e:
        if "asyncio.run()" in str(e) and "running event loop" in str(e).lower():
            logger.warning("Event loop aktiv – Orchestration-Override empfohlen: %s", e)
        raise RuntimeError(
            "Orchestrierung aus Workflow erfordert asyncio.run oder set_workflow_orchestration_override (Tests)."
        ) from e
