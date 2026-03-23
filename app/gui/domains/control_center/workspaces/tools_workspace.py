"""
ToolsWorkspace – Übersicht eingebauter Tools und Konfigurationsstatus.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel
from app.gui.domains.control_center.workspaces.base_management_workspace import BaseManagementWorkspace
from app.gui.domains.control_center.panels.tools_panels import (
    ToolRegistryPanel,
    ToolSummaryPanel,
)
from app.services.infrastructure_snapshot import build_tool_snapshot_rows


class ToolsWorkspace(BaseManagementWorkspace):
    """Workspace: Tool-Übersicht (Live aus AppSettings / eingebaute Module)."""

    def __init__(self, parent=None):
        super().__init__("cc_tools", parent)
        self._registry: ToolRegistryPanel | None = None
        self._summary: ToolSummaryPanel | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self._registry = ToolRegistryPanel(self)
        self._summary = ToolSummaryPanel(self)
        content_layout.addWidget(self._registry)
        content_layout.addWidget(self._summary)

        detail = QFrame()
        detail.setObjectName("toolDetailArea")
        detail.setStyleSheet(
            "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
            "min-height: 100px; padding: 16px;"
        )
        dl = QVBoxLayout(detail)
        dl.setContentsMargins(16, 16, 16, 16)
        title = QLabel("Hinweis")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        dl.addWidget(title)
        n = len(build_tool_snapshot_rows())
        label = QLabel(
            f"Aktuell {n} Zeilen aus Produktcode und Einstellungen. "
            "Keine zentrale Plugin-Registry; Erweiterungen erfolgen über Codepfade."
        )
        label.setWordWrap(True)
        label.setStyleSheet("color: #64748b; font-size: 12px;")
        dl.addWidget(label)
        content_layout.addWidget(detail)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Tool-spezifischen Inspector. D9: content_token optional."""
        self._inspector_host = inspector_host
        from app.gui.inspector.tool_inspector import ToolInspector

        rows = build_tool_snapshot_rows()
        if rows:
            r = rows[0]
            content = ToolInspector(
                tool=r.tool_id,
                category=r.category,
                permissions=r.permissions,
                availability=r.status,
            )
        else:
            content = ToolInspector()
        inspector_host.set_content(content, content_token=content_token)
