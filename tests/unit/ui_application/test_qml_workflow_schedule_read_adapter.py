"""ServiceQmlWorkflowScheduleReadAdapter — schmale Abbildung auf ScheduleListRow."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.ui_application.adapters.service_qml_workflow_schedule_read_adapter import (
    ServiceQmlWorkflowScheduleReadAdapter,
)
from app.workflows.scheduling.models import ScheduleListRow, WorkflowSchedule


def test_adapter_maps_list_schedules_rows() -> None:
    sch = WorkflowSchedule(
        schedule_id="s1",
        workflow_id="wf",
        enabled=True,
        initial_input_json="{}",
        next_run_at="2099-01-01T00:00:00+00:00",
        last_fired_at=None,
        created_at="",
        updated_at="",
        rule_json="{}",
    )
    row = ScheduleListRow(schedule=sch, workflow_name="My WF")
    mock_svc = MagicMock()
    mock_svc.list_schedules.return_value = [row]

    with patch(
        "app.ui_application.adapters.service_qml_workflow_schedule_read_adapter.get_schedule_service",
        return_value=mock_svc,
    ):
        ad = ServiceQmlWorkflowScheduleReadAdapter()
        out = ad.list_schedule_summaries(project_scope_id=3, include_global=True)

    mock_svc.list_schedules.assert_called_once_with(project_scope_id=3, include_global=True)
    assert out == [
        {
            "scheduleId": "s1",
            "workflowId": "wf",
            "workflowName": "My WF",
            "enabled": True,
            "nextRunAt": "2099-01-01T00:00:00+00:00",
        }
    ]
