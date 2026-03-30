"""Start-Knoten: liefert initial_input."""

from __future__ import annotations

import copy
from typing import Any, Dict, Optional

from app.workflows.execution.context import RunContext
from app.workflows.execution.node_executors.base import BaseNodeExecutor
from app.workflows.models.definition import WorkflowNode


class StartNodeExecutor(BaseNodeExecutor):
    """Ignoriert Vorgänger; gibt eine Kopie von context.initial_input zurück."""

    def execute(
        self,
        node: WorkflowNode,
        input_payload: Optional[Dict[str, Any]],
        context: RunContext,
    ) -> Dict[str, Any]:
        return copy.deepcopy(dict(context.initial_input))
