"""Adapter: :class:`QmlWorkflowScheduleReadPort` → :class:`ScheduleService.list_schedules`."""

from __future__ import annotations

from typing import Any, Optional

from app.services.schedule_service import get_schedule_service


class ServiceQmlWorkflowScheduleReadAdapter:
    def list_schedule_summaries(
        self,
        *,
        project_scope_id: Optional[int],
        include_global: bool,
    ) -> list[dict[str, Any]]:
        rows = get_schedule_service().list_schedules(
            project_scope_id=project_scope_id,
            include_global=include_global,
        )
        out: list[dict[str, Any]] = []
        for r in rows:
            s = r.schedule
            out.append(
                {
                    "scheduleId": s.schedule_id,
                    "workflowId": s.workflow_id,
                    "workflowName": r.workflow_name or "",
                    "enabled": bool(s.enabled),
                    "nextRunAt": s.next_run_at or "",
                }
            )
        return out
