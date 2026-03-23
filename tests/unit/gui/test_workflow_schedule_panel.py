"""R3: WorkflowSchedulePanel Smoke (kein Langläufer im UI-Thread)."""

from __future__ import annotations

from unittest.mock import MagicMock

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.workflows.panels.workflow_schedule_panel import WorkflowSchedulePanel
from app.workflows.scheduling.models import ScheduleListRow, WorkflowSchedule


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_workflow_schedule_panel_instantiable():
    _app()
    panel = WorkflowSchedulePanel()
    panel.set_schedules([])
    assert panel._table.rowCount() == 0


def test_jump_to_run_requested_uses_resolver():
    _app()
    panel = WorkflowSchedulePanel()
    mock = MagicMock(return_value="run_z")
    panel.set_last_run_resolver(mock)
    sch = WorkflowSchedule(
        schedule_id="sched_1",
        workflow_id="w1",
        enabled=True,
        initial_input_json="{}",
        next_run_at="2030-01-01T00:00:00+00:00",
        last_fired_at=None,
        created_at="2030-01-01T00:00:00+00:00",
        updated_at="2030-01-01T00:00:00+00:00",
        rule_json="{}",
    )
    panel.set_schedules([ScheduleListRow(schedule=sch, workflow_name="N")])
    panel._table.selectRow(0)
    received: list[str] = []
    panel.jump_to_run_requested.connect(lambda rid: received.append(rid))
    assert panel._btn_jump.isEnabled()
    QTest.mouseClick(panel._btn_jump, Qt.MouseButton.LeftButton)
    assert received == ["run_z"]
    mock.assert_called_with("sched_1")


def test_run_now_requested_emits_schedule_id():
    _app()
    panel = WorkflowSchedulePanel()
    sch = WorkflowSchedule(
        schedule_id="sched_2",
        workflow_id="w2",
        enabled=True,
        initial_input_json="{}",
        next_run_at="2030-01-01T00:00:00+00:00",
        last_fired_at=None,
        created_at="2030-01-01T00:00:00+00:00",
        updated_at="2030-01-01T00:00:00+00:00",
        rule_json="{}",
    )
    panel.set_schedules([ScheduleListRow(schedule=sch, workflow_name="")])
    panel._table.selectRow(0)
    got: list[str] = []
    panel.run_now_requested.connect(lambda sid: got.append(sid))
    QTest.mouseClick(panel._btn_run, Qt.MouseButton.LeftButton)
    assert got == ["sched_2"]
