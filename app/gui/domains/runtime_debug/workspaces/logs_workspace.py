"""
LogsWorkspace – Log Stream, Filter, Log Detail mit echten Logs.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.gui.domains.runtime_debug.workspaces.base_monitoring_workspace import BaseMonitoringWorkspace
from app.gui.domains.runtime_debug.panels.logs_panels import LogStreamPanel, LogDetailPanel


class LogsWorkspace(BaseMonitoringWorkspace):
    """Workspace für Logs – echte Python-Logs."""

    def __init__(self, parent=None):
        super().__init__("rd_logs", parent)
        self._inspector_host = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self._stream = LogStreamPanel(self)
        self._detail = LogDetailPanel(self)
        content_layout.addWidget(self._stream)
        content_layout.addWidget(self._detail)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #0f172a; border: none; }")
        layout.addWidget(scroll)

    def on_log_selected(self, entry) -> None:
        self._detail.set_entry(entry)
        self._refresh_inspector(entry)

    def _refresh_inspector(self, entry, content_token: int | None = None) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.log_inspector import LogInspector
        if entry:
            content = LogInspector(
                timestamp=entry.timestamp.strftime("%H:%M:%S") if entry.timestamp else "—",
                level=entry.level,
                module=entry.module or "—",
                message=(entry.message or "")[:200],
            )
        else:
            content = LogInspector(timestamp="—", level="—", module="—", message="Log auswählen…")
        self._inspector_host.set_content(content, content_token=content_token)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """D9: content_token optional."""
        self._inspector_host = inspector_host
        self._refresh_inspector(None, content_token=content_token)
