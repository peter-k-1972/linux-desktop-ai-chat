"""Privacy settings category – telemetry, data handling."""

from PySide6.QtWidgets import QVBoxLayout, QFrame, QLabel, QScrollArea
from PySide6.QtCore import Qt

from app.gui.domains.settings.categories.base_category import BaseSettingsCategory


class PrivacyCategory(BaseSettingsCategory):
    """Privacy settings: telemetry, data retention."""

    def __init__(self, parent=None):
        super().__init__("settings_privacy", parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        inner = QFrame()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(16)

        panel = QFrame()
        panel.setObjectName("settingsPanel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(16, 16, 16, 16)
        t = QLabel("Privacy")
        t.setObjectName("settingsPanelTitle")
        pl.addWidget(t)
        l = QLabel(
            "Telemetrie, Datenspeicherung, API-Keys. "
            "Alle Daten bleiben lokal, es werden keine externen Dienste genutzt. "
            "API-Keys (z.B. Ollama Cloud) können im Legacy-Settings-Dialog oder über .env gesetzt werden."
        )
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
