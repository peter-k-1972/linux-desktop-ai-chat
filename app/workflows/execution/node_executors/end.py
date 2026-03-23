"""End-Knoten: setzt final_output am Kontext."""

from __future__ import annotations

import copy
from typing import Any, Dict, Optional

from app.workflows.execution.context import RunContext
from app.workflows.execution.node_executors.base import BaseNodeExecutor
from app.workflows.models.definition import WorkflowNode


class EndNodeExecutor(BaseNodeExecutor):
    """Übernimmt Eingabe als Run-Endergebnis."""

    def execute(
        self,
        node: WorkflowNode,
        input_payload: Optional[Dict[str, Any]],
        context: RunContext,
    ) -> Dict[str, Any]:
        data = copy.deepcopy(dict(input_payload or {}))
        context.final_output = copy.deepcopy(data)
        return data
