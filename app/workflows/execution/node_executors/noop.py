"""Noop-Knoten: durchreichen, optional config.merge flach einmischen."""

from __future__ import annotations

import copy
from typing import Any, Dict, Optional

from app.workflows.execution.context import RunContext
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
        merge = node.config.get("merge")
        if isinstance(merge, dict):
            for k, v in merge.items():
                out[k] = copy.deepcopy(v)
        return out
