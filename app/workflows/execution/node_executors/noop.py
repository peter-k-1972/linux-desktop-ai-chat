"""Noop-Knoten: durchreichen, optional config.merge flach einmischen."""

from __future__ import annotations

import copy
import logging
from typing import Any, Dict, Optional

from app.workflows.execution.context import RunContext

logger = logging.getLogger(__name__)
from app.workflows.execution.node_executors.base import BaseNodeExecutor
from app.workflows.models.definition import WorkflowNode


class NoopNodeExecutor(BaseNodeExecutor):
    """
    Gibt input_payload zurück.
    Wenn config.merge gesetzt ist: flaches Update auf die Kopie der Eingabe.
    """

    def execute(
        self,
        node: WorkflowNode,
        input_payload: Optional[Dict[str, Any]],
        context: RunContext,
    ) -> Dict[str, Any]:
        out = copy.deepcopy(dict(input_payload or {}))
        cfg = dict(node.config or {})
        merge = cfg.get("merge")
        if isinstance(merge, dict):
            for k, v in merge.items():
                out[k] = copy.deepcopy(v)

        snap = cfg.get("snapshot_response_as")
        if isinstance(snap, str) and snap.strip():
            rt = out.get("response_text")
            if isinstance(rt, str):
                out[snap.strip()] = rt
                logger.info("noop: snapshot_response_as -> %s (%d chars)", snap.strip(), len(rt))

        ctra = cfg.get("copy_tool_result_as")
        if isinstance(ctra, str) and ctra.strip():
            tr = out.get("tool_result")
            if tr is not None:
                out[ctra.strip()] = copy.deepcopy(tr)
                logger.info("noop: copy_tool_result_as -> %s", ctra.strip())

        stsa = cfg.get("snapshot_tool_success_as")
        if isinstance(stsa, str) and stsa.strip():
            tr = out.get("tool_result")
            if isinstance(tr, dict):
                out[stsa.strip()] = bool(tr.get("success"))
                logger.info("noop: snapshot_tool_success_as %s=%s", stsa.strip(), out[stsa.strip()])

        return out
