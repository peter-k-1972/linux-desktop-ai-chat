"""Application settings category – app info, runtime status."""

from PySide6.QtWidgets import QVBoxLayout, QFrame, QLabel, QScrollArea
from PySide6.QtCore import Qt

from app.gui.domains.settings.categories.base_category import BaseSettingsCategory


class ApplicationCategory(BaseSettingsCategory):
    """Application settings: info, runtime, system options."""

    def __init__(self, parent=None):
        super().__init__("settings_application", parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = [
            ("Application Info", "Linux Desktop Chat · Shell · v0.1"),
            ("Runtime Status", "Bereit. Backend-Verbindung wird bei Bedarf hergestellt."),
            ("System", "Weitere Systemoptionen werden bei Bedarf ergänzt."),
        ]

        inner = QFrame()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(16)

        for title, text in content:
            panel = QFrame()
            panel.setObjectName("settingsPanel")
            pl = QVBoxLayout(panel)
            pl.setContentsMargins(16, 16, 16, 16)
            t = QLabel(title)
            t.setObjectName("settingsPanelTitle")
            pl.addWidget(t)
            l = QLabel(text)
            l.setObjectName("settingsPanelDescription")
            l.setWordWrap(True)
            pl.addWidget(l)
            inner_layout.addWidget(panel)
        inner_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setWidget(inner)
        layout.addWidget(scroll, 1)
