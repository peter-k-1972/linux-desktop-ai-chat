"""
BaseSettingsWorkspace – Basis für Settings-Workspaces.

Appearance, System, Models, Agents, Advanced.
"""

from PySide6.QtWidgets import QWidget


class BaseSettingsWorkspace(QWidget):
    """Basis für Settings-Workspaces."""

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
