"""tool_call: Pipeline StepExecutor-Registry (sync), keine Shell-Erweiterung."""

from __future__ import annotations

import copy
import logging
from typing import Any, Dict, Optional

from app.pipelines import get_executor_registry

logger = logging.getLogger(__name__)

_CURSOR_LIGHT_CTX_KEYS = frozenset(
    {
        "mode",
        "path",
        "old_text",
        "new_text",
        "patch",
        "strip",
        "timeout_sec",
        "command_key",
        "args",
        "pattern",
        "literal",
        "include_glob",
        "exclude_glob",
        "max_matches",
        "porcelain",
        "scope",
        "max_chars",
        "encoding",
        "line_start",
        "line_end",
        "max_bytes",
        "max_lines",
        "create_dirs",
        "content",
    }
)


def _merge_cursor_light_executor_config(exec_cfg: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    ec = copy.deepcopy(dict(exec_cfg or {}))
    if not str(ec.get("workspace_root") or "").strip() and str(ctx.get("workspace_root") or "").strip():
        ec["workspace_root"] = str(ctx.get("workspace_root")).strip()
    base_in = dict(ec.get("input") or {})
    for k in _CURSOR_LIGHT_CTX_KEYS:
        if k in ctx:
            base_in[k] = ctx[k]
    ec["input"] = base_in
    return ec
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
        if et == "cursor_light":
            exec_cfg = _merge_cursor_light_executor_config(exec_cfg, ctx)
            logger.info(
                "tool_call cursor_light tool_id=%s workspace=%s",
                exec_cfg.get("tool_id"),
                exec_cfg.get("workspace_root") or ctx.get("workspace_root"),
            )

        step_id = str(cfg.get("step_id") or node.node_id)
        sr = executor.execute(step_id, exec_cfg, ctx)

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
        out = copy.deepcopy(dict(input_payload or {}))
        out["tool_result"] = dict(sr.output or {})
        out["logs"] = list(sr.logs or [])
        out["artifacts"] = arts
        merge_out = bool(cfg.get("merge_step_output_into_payload"))
        if merge_out and isinstance(sr.output, dict):
            for k, v in sr.output.items():
                out[k] = copy.deepcopy(v)

        if not sr.success:
            out["tool_call_success"] = False
            out["tool_call_error"] = sr.error or "Tool-Ausführung fehlgeschlagen."
            logger.warning(
                "tool_call soft-fail executor_type=%s step=%s error=%s",
                et,
                step_id,
                out["tool_call_error"],
            )
            return out

        out["tool_call_success"] = True
        if bool(cfg.get("replace_payload_with_tool_output")) and isinstance(sr.output, dict):
            slim: Dict[str, Any] = copy.deepcopy(dict(sr.output or {}))
            slim["tool_result"] = copy.deepcopy(dict(sr.output or {}))
            slim["logs"] = list(sr.logs or [])
            slim["artifacts"] = arts
            slim["tool_call_success"] = True
            logger.info(
                "tool_call slim payload executor_type=%s keys=%s",
                et,
                sorted(k for k in slim if k not in ("logs", "artifacts", "tool_result")),
            )
            return slim

        logger.info("tool_call done executor_type=%s log_lines=%d", et, len(out["logs"]))
        return out
