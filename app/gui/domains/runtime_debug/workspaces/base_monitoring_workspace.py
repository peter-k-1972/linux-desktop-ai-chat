"""
BaseMonitoringWorkspace – Basis für Runtime-/Debug-Workspaces.

EventBus, Logs, Metrics, LLM Calls, Agent Activity, System Graph.
Einheitliche Schnittstelle: setup_inspector(inspector_host).
"""

from PySide6.QtWidgets import QWidget


class BaseMonitoringWorkspace(QWidget):
    """Basis für Monitoring- und Debug-Workspaces."""

    def __init__(self, workspace_id: str, parent=None):
        super().__init__(parent)
        self._workspace_id = workspace_id
        self._inspector_host = None
        self.setObjectName(f"{workspace_id}Workspace")

    @property
    def workspace_id(self) -> str:
        """Eindeutige ID des Workspaces."""
        return self._workspace_id

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt den Inspector-Inhalt. Override in Subklassen. D9: content_token optional."""
        self._inspector_host = inspector_host
        inspector_host.clear_content()
