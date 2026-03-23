"""
BaseOperationsWorkspace – Basis für Operations-Unterworkspaces.

Einheitliche Schnittstelle: setup_inspector(inspector_host, content_token=…).
"""

from typing import Optional

from PySide6.QtWidgets import QWidget


class BaseOperationsWorkspace(QWidget):
    """Basis für Chat, Agent Tasks, Knowledge, Prompt Studio."""

    def __init__(self, workspace_id: str, parent=None):
        super().__init__(parent)
        self._workspace_id = workspace_id
        self.setObjectName(f"{workspace_id}Workspace")

    @property
    def workspace_id(self) -> str:
        """Eindeutige ID des Workspaces."""
        return self._workspace_id

    def setup_inspector(
        self, inspector_host, content_token: Optional[int] = None
    ) -> None:
        """Setzt den Inspector-Inhalt. Override in Subklassen; content_token vom WorkspaceHost."""
        inspector_host.clear_content()
