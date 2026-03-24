"""Appearance settings category – theme, UI options."""

from PySide6.QtWidgets import QVBoxLayout, QScrollArea, QFrame
from PySide6.QtCore import Qt

from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter

from app.gui.domains.settings.categories.base_category import BaseSettingsCategory
from app.gui.domains.settings.panels.theme_selection_panel import ThemeSelectionPanel


class AppearanceCategory(BaseSettingsCategory):
    """Appearance settings: theme selection, UI preferences."""

    def __init__(self, parent=None):
        super().__init__("settings_appearance", parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(ThemeSelectionPanel(self, appearance_port=ServiceSettingsAdapter()))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
