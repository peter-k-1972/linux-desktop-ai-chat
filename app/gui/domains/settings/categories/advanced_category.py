"""Advanced settings category – debug, experimental."""

from PySide6.QtWidgets import QVBoxLayout, QFrame, QScrollArea
from PySide6.QtCore import Qt

from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter

from app.gui.domains.settings.categories.base_category import BaseSettingsCategory
from app.gui.domains.settings.panels.advanced_settings_panel import AdvancedSettingsPanel


class AdvancedCategory(BaseSettingsCategory):
    """Advanced settings: debug flags, experimental features."""

    def __init__(self, parent=None):
        super().__init__("settings_advanced", parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(AdvancedSettingsPanel(self, settings_port=ServiceSettingsAdapter()))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
