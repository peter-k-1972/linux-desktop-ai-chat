"""Workflow-Ausführung.

WorkflowExecutor wird bewusst nicht hier importiert (vermeidet Zyklen mit der Registry).
Verwenden: ``from app.workflows.execution.executor import WorkflowExecutor``.
"""

from app.workflows.execution.context import AbortToken, RunContext

__all__ = ["AbortToken", "RunContext"]
