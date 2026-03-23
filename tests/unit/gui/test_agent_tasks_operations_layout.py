"""R2: Agent Tasks Workspace mit Betrieb-Tab."""

from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import AgentTasksWorkspace


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_agent_tasks_workspace_builds_with_tabs():
    _app()
    with patch.object(AgentTasksWorkspace, "_defer_init", lambda self: None):
        w = AgentTasksWorkspace()
    assert w._tabs.count() == 2
    assert w._tabs.tabText(0) == "Betrieb"
    assert w._tabs.tabText(1) == "Aufgaben"


def test_agent_tasks_open_with_context_switches_tab():
    _app()
    with patch.object(AgentTasksWorkspace, "_defer_init", lambda self: None):
        with patch.object(AgentTasksWorkspace, "_refresh_agents", lambda self: None):
            w = AgentTasksWorkspace()
            w.open_with_context({"agent_ops_subtab": "tasks"})
            assert w._tabs.currentIndex() == 1
