"""
SystemWorkspace – Application Info, Runtime Status, Systemoptionen.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFrame,
    QLabel,
    QScrollArea,
)
from app.gui.domains.settings.workspaces.base_settings_workspace import BaseSettingsWorkspace


def _panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class SystemWorkspace(BaseSettingsWorkspace):
    """Workspace für System-Einstellungen."""

    def __init__(self, parent=None):
        super().__init__("settings_system", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        for title, text in [
            ("Application Info", "Linux Desktop Chat · Shell · v0.1"),
            ("Runtime Status", "Bereit · Keine Backend-Verbindung"),
            ("Zukünftige Optionen", "Systemoptionen werden hier erscheinen."),
        ]:
            panel = QFrame()
            panel.setStyleSheet(_panel_style())
            pl = QVBoxLayout(panel)
            pl.setContentsMargins(16, 16, 16, 16)
            t = QLabel(title)
            t.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
            pl.addWidget(t)
            l = QLabel(text)
            l.setStyleSheet("color: #64748b; font-size: 12px;")
            l.setWordWrap(True)
            pl.addWidget(l)
            content_layout.addWidget(panel)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt System-Info im Inspector. D9: content_token optional."""
        self._inspector_host = inspector_host
        from app.gui.inspector.system_settings_inspector import SystemSettingsInspector
        content = SystemSettingsInspector()
        inspector_host.set_content(content, content_token=content_token)
