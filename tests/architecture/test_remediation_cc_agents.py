"""
Regression: Control-Center Agents = AgentManagerPanel (Doku-vs-Code).

Verhindert Rückfall auf entferntes agents_panels-Demo.
"""

from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.gui.domains.control_center.workspaces.agents_workspace import AgentsWorkspace
from app.gui.domains.control_center.agents_ui.agent_manager_panel import AgentManagerPanel


def test_agents_workspace_uses_agent_manager_panel(qapplication):
    w = AgentsWorkspace()
    w.show()
    QApplication.processEvents()
    assert w._panel is not None
    assert isinstance(w._panel, AgentManagerPanel)


def test_agents_panels_module_removed():
    root = Path(__file__).resolve().parents[2]
    dead = root / "app" / "gui" / "domains" / "control_center" / "panels" / "agents_panels.py"
    assert not dead.exists(), "Demo agents_panels.py sollte nicht wieder auftauchen"


def test_control_center_panels_export_no_demo_agent_classes():
    import app.gui.domains.control_center.panels as cc_panels

    assert "AgentRegistryPanel" not in cc_panels.__all__
    assert "AgentSummaryPanel" not in cc_panels.__all__
