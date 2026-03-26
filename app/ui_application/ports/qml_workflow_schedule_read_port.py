"""
Rein lesender Workflow-Schedule-Zugriff für QML (kein CRUD, kein Tick).
"""

from __future__ import annotations

from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class QmlWorkflowScheduleReadPort(Protocol):
    def list_schedule_summaries(
        self,
        *,
        project_scope_id: Optional[int],
        include_global: bool,
    ) -> list[dict[str, Any]]:
        """
        Schlankes Tabellenmodell für die View.

        Erwartete Schlüssel pro Zeile: ``scheduleId``, ``workflowId``, ``workflowName``,
        ``enabled`` (bool), ``nextRunAt`` (str).
        """
