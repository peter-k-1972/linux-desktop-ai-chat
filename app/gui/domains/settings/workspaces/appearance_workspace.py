"""
AppearanceWorkspace – Theme-Auswahl und UI-Einstellungen.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter

from app.gui.domains.settings.workspaces.base_settings_workspace import BaseSettingsWorkspace
from app.gui.domains.settings.panels.theme_selection_panel import ThemeSelectionPanel
from app.gui.themes import get_theme_manager


class AppearanceWorkspace(BaseSettingsWorkspace):
    """Workspace für Appearance (Theme, UI-Einstellungen)."""

    def __init__(self, parent=None):
        super().__init__("settings_appearance", parent)
        self._setup_ui()
        get_theme_manager().theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_id: str) -> None:
        """Aktualisiert den Inspector und Icon-Cache bei Theme-Wechsel."""
        from app.gui.icons import IconManager
        IconManager.clear_cache()
        if self._inspector_host:
            from app.gui.inspector.appearance_inspector import AppearanceInspector
            content = AppearanceInspector(theme_id=theme_id)
            self._inspector_host.set_content(content)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(ThemeSelectionPanel(self, appearance_port=ServiceSettingsAdapter()))

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Theme-Details im Inspector. D9: content_token optional."""
        self._inspector_host = inspector_host
        from app.gui.inspector.appearance_inspector import AppearanceInspector
        from app.gui.themes import get_theme_manager
        current = get_theme_manager().get_current_id()
        content = AppearanceInspector(theme_id=current)
        inspector_host.set_content(content, content_token=content_token)
