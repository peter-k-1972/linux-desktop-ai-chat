"""context_load: ContextExplainService über workflow_context_adapter (keine GUI)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.workflow_context_adapter import build_workflow_context_bundle
from app.workflows.execution.context import RunContext
from app.workflows.execution.node_executors.base import BaseNodeExecutor
from app.workflows.models.definition import WorkflowNode


def _pick(cfg: dict, inp: Optional[Dict[str, Any]], key: str) -> Any:
    if inp and key in inp and inp[key] is not None:
        return inp[key]
    return cfg.get(key)


def _resolve_chat_id(cfg: dict, inp: Optional[Dict[str, Any]]) -> int:
    cid = _pick(cfg, inp, "chat_id")
    if cid is None:
        raise ValueError("context_load: chat_id in config oder Eingabe (chat_id) erforderlich.")
    try:
        n = int(cid)
    except (TypeError, ValueError) as e:
        raise ValueError("context_load: chat_id muss eine ganze Zahl sein.") from e
    if n < 1:
        raise ValueError("context_load: chat_id muss >= 1 sein.")
    return n


class ContextLoadNodeExecutor(BaseNodeExecutor):
    def execute(
        self,
        node: WorkflowNode,
        input_payload: Optional[Dict[str, Any]],
        context: RunContext,
    ) -> Dict[str, Any]:
        cfg = dict(node.config or {})
        inp = dict(input_payload or {})

        chat_id = _resolve_chat_id(cfg, inp)
        hint = _pick(cfg, inp, "request_context_hint")
        policy = _pick(cfg, inp, "context_policy")
        hint_s = str(hint).strip() if hint is not None else None
        policy_s = str(policy).strip() if policy is not None else None
        if hint_s == "":
            hint_s = None
        if policy_s == "":
            policy_s = None

        inc_pp = cfg.get("include_payload_preview", True)
        if isinstance(inp.get("include_payload_preview"), bool):
            inc_pp = inp["include_payload_preview"]
        inc_tr = cfg.get("include_trace", False)
        if isinstance(inp.get("include_trace"), bool):
            inc_tr = inp["include_trace"]

        bundle = build_workflow_context_bundle(
            chat_id,
            request_context_hint=hint_s,
            context_policy=policy_s,
            include_payload_preview=bool(inc_pp),
            include_trace=bool(inc_tr),
        )
        expl = bundle.get("context_payload")
        if isinstance(expl, dict) and expl.get("failsafe_triggered"):
            reason = expl.get("empty_result_reason") or "failsafe"
            raise RuntimeError(f"context_load: Kontext-Auflösung fehlgeschlagen ({reason}).")
        return bundle
