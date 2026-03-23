"""Laufzeitkontext für die Workflow-Ausführung."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.workflows.models.definition import WorkflowDefinition


@dataclass
class AbortToken:
    """Kooperativer Abbruch zwischen Knoten."""

    _cancelled: bool = False

    def cancel(self) -> None:
        self._cancelled = True

    def is_cancelled(self) -> bool:
        return self._cancelled

    def reset(self) -> None:
        self._cancelled = False


@dataclass
class RunContext:
    """Zustand während eines Runs (keine Persistenz)."""

    run_id: str
    definition: WorkflowDefinition
    initial_input: Dict[str, Any]
    abort: AbortToken
    node_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    final_output: Optional[Dict[str, Any]] = None

    def set_output(self, node_id: str, payload: Dict[str, Any]) -> None:
        self.node_outputs[node_id] = copy.deepcopy(payload)

    def get_output(self, node_id: str) -> Optional[Dict[str, Any]]:
        raw = self.node_outputs.get(node_id)
        return copy.deepcopy(raw) if raw is not None else None
