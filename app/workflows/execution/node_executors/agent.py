"""agent: AgentTaskRunner über workflow_agent_adapter (keine GUI)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.workflow_agent_adapter import run_workflow_agent
from app.workflows.execution.context import RunContext
from app.workflows.execution.node_executors.base import BaseNodeExecutor
from app.workflows.models.definition import WorkflowNode


def resolve_workflow_agent_id(config: dict) -> str:
    aid = config.get("agent_id")
    if aid is not None and str(aid).strip():
        return str(aid).strip()
    slug = config.get("agent_slug")
    if slug is not None and str(slug).strip():
        from app.agents.agent_service import get_agent_service

        profile = get_agent_service().get_by_slug(str(slug).strip())
        if profile is None or not (profile.id or "").strip():
            raise ValueError(f"Kein Agent mit agent_slug={slug!r}.")
        return str(profile.id)
    raise ValueError("agent: agent_id oder agent_slug erforderlich.")


def extract_agent_prompt(input_payload: Optional[Dict[str, Any]]) -> str:
    if not input_payload:
        raise ValueError("agent: Eingabe fehlt (erwartet u. a. prompt_text).")
    for key in ("prompt_text", "prompt", "message", "text", "user_input", "context_text"):
        v = input_payload.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    raise ValueError(
        "agent: in der Eingabe fehlt ein Textfeld prompt_text (oder prompt / message / text)."
    )


class AgentNodeExecutor(BaseNodeExecutor):
    def execute(
        self,
        node: WorkflowNode,
        input_payload: Optional[Dict[str, Any]],
        context: RunContext,
    ) -> Dict[str, Any]:
        cfg = dict(node.config or {})
        agent_id = resolve_workflow_agent_id(cfg)
        prompt = extract_agent_prompt(input_payload)
        model_override = cfg.get("model_override")
        if model_override is not None:
            model_override = str(model_override).strip() or None

        result = run_workflow_agent(agent_id, prompt, model_override)
        if not result.get("success"):
            err = result.get("error") or "Agent-Lauf fehlgeschlagen."
            raise RuntimeError(err)

        return {
            "response_text": str(result.get("response_text") or ""),
            "task_id": result.get("task_id"),
            "metadata": dict(result.get("metadata") or {}),
        }
