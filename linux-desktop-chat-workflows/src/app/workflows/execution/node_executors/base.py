"""Basisklasse für Knoten-Executoren."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from app.workflows.execution.context import RunContext
    from app.workflows.models.definition import WorkflowNode


class BaseNodeExecutor(ABC):
    """Ein Executor führt genau einen Knotentyp aus (ohne I/O, ohne Qt)."""

    @abstractmethod
    def execute(
        self,
        node: WorkflowNode,
        input_payload: Optional[Dict[str, Any]],
        context: RunContext,
    ) -> Dict[str, Any]:
        """
        Args:
            node: Knotendefinition
            input_payload: None beim Start-Knoten; sonst zusammengesetztes Input-Dict
            context: Laufzeitkontext

        Returns:
            JSON-ähnliches Dict (nur serialisierbare Werte)
        """
        raise NotImplementedError
