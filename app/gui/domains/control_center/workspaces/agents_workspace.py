"""
AgentsWorkspace – Verwaltungssicht auf Agenten.

Hosts AgentManagerPanel (canonical). Inspector bound to agent selection.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout

from app.gui.domains.control_center.workspaces.base_management_workspace import BaseManagementWorkspace
from app.gui.domains.control_center.agents_ui import AgentManagerPanel


class AgentsWorkspace(BaseManagementWorkspace):
    """Workspace für Agent-Verwaltung. Hosts AgentManagerPanel. D27: Inspector bound to selection."""

    def __init__(self, parent=None):
        super().__init__("cc_agents", parent)
        self._panel: AgentManagerPanel | None = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._panel = AgentManagerPanel(theme="dark")
        layout.addWidget(self._panel)

    def _connect_signals(self) -> None:
        if self._panel and self._panel.list_panel:
            self._panel.list_panel.agent_selected.connect(self._on_agent_selected)

    def _on_agent_selected(self, profile) -> None:
        """D27: Updates Inspector when user selects an agent."""
        if profile is None:
            self._refresh_inspector("(keine Auswahl)", "—", "—", "—", "—")
            return
        name = getattr(profile, "effective_display_name", None) or getattr(profile, "display_name", None) or getattr(profile, "name", "(keine)")
        role = getattr(profile, "department", "—") or "—"
        model = getattr(profile, "assigned_model", None) or getattr(profile, "model_id", "—") or "—"
        tools = getattr(profile, "tools", None)
        tool_str = ", ".join(tools) if isinstance(tools, list) else str(tools or "—")
        status = getattr(profile, "status", "—") or "—"
        self._refresh_inspector(str(name), str(role), str(model), tool_str, str(status))

    def _refresh_inspector(
        self,
        agent: str = "(keine Auswahl)",
        role: str = "—",
        model: str = "—",
        tools: str = "—",
        status: str = "—",
        content_token: int | None = None,
    ) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.agent_inspector import AgentInspector
        content = AgentInspector(
            agent=agent,
            role=role,
            model_binding=model,
            toolset=tools,
            status=status,
        )
        self._inspector_host.set_content(content, content_token=content_token)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Agent-spezifischen Inspector. D9: content_token optional. D27: Placeholder until selection."""
        self._inspector_host = inspector_host
        self._refresh_inspector(
            agent="(keine Auswahl)",
            role="—",
            model="—",
            tools="—",
            status="—",
            content_token=content_token,
        )
