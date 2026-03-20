"""
ToolsWorkspace – Verwaltung von Tools.

Tool Registry, Status, Categories, Permissions, Detailbereich.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel
from app.gui.domains.control_center.workspaces.base_management_workspace import BaseManagementWorkspace
from app.gui.domains.control_center.panels.tools_panels import (
    ToolRegistryPanel,
    ToolSummaryPanel,
)


class ToolsWorkspace(BaseManagementWorkspace):
    """Workspace für Tool-Verwaltung."""

    def __init__(self, parent=None):
        super().__init__("cc_tools", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(ToolRegistryPanel(self))
        content_layout.addWidget(ToolSummaryPanel(self))

        detail = QFrame()
        detail.setObjectName("toolDetailArea")
        detail.setStyleSheet(
            "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
            "min-height: 100px; padding: 16px;"
        )
        dl = QVBoxLayout(detail)
        dl.setContentsMargins(16, 16, 16, 16)
        title = QLabel("Permissions / Availability")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        dl.addWidget(title)
        label = QLabel("7 Tools verfügbar · 5 Kategorien · Alle berechtigt")
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
        content = ToolInspector(
            tool="web_search",
            category="Search",
            permissions="Read",
            availability="Available",
        )
        inspector_host.set_content(content, content_token=content_token)
