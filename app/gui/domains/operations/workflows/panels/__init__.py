"""Workflow-GUI-Panels."""

from app.gui.domains.operations.workflows.panels.workflow_editor_panel import WorkflowEditorPanel
from app.gui.domains.operations.workflows.panels.workflow_inspector_panel import WorkflowInspectorPanel
from app.gui.domains.operations.workflows.panels.workflow_list_panel import WorkflowListPanel
from app.gui.domains.operations.workflows.panels.workflow_run_panel import WorkflowRunPanel
from app.gui.domains.operations.workflows.panels.workflow_schedule_panel import WorkflowSchedulePanel

__all__ = [
    "WorkflowListPanel",
    "WorkflowEditorPanel",
    "WorkflowInspectorPanel",
    "WorkflowRunPanel",
    "WorkflowSchedulePanel",
]
