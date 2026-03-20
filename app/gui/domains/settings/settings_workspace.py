"""
SettingsWorkspace – Full-page settings with left nav, center content, right help.

Layout: Left (categories) | Center (content) | Right (help, optional)
Extendable: categories and content components are registered separately.
"""

from typing import Callable, Dict, Optional, Type

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QStackedWidget,
    QFrame,
    QLabel,
    QSizePolicy,
)
from PySide6.QtCore import Qt

from app.gui.domains.settings.navigation import SettingsNavigation
from app.gui.domains.settings.categories import (
    ApplicationCategory,
    AppearanceCategory,
    AIModelsCategory,
    DataCategory,
    PrivacyCategory,
    AdvancedCategory,
    ProjectCategory,
    WorkspaceCategory,
)


# Extendable: category_id -> widget class (or factory)
# Structure: Application | Project | Workspace
_category_factories: Dict[str, Type[QWidget]] = {
    "settings_application": ApplicationCategory,
    "settings_appearance": AppearanceCategory,
    "settings_ai_models": AIModelsCategory,
    "settings_data": DataCategory,
    "settings_privacy": PrivacyCategory,
    "settings_advanced": AdvancedCategory,
    "settings_project": ProjectCategory,
    "settings_workspace": WorkspaceCategory,
}


def register_settings_category_widget(category_id: str, widget_class: Type[QWidget]) -> None:
    """Register a widget class for a settings category. Extendable API."""
    _category_factories[category_id] = widget_class


def get_category_widget(category_id: str, parent: Optional[QWidget] = None) -> Optional[QWidget]:
    """Create and return the widget for a category."""
    factory = _category_factories.get(category_id)
    if factory:
        return factory(parent)
    return None


class SettingsHelpPanel(QFrame):
    """Optional right-side help panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsHelpPanel")
        self.setMinimumWidth(200)
        self.setMaximumWidth(320)
        self._setup_ui()

    def _setup_ui(self) -> None:
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(8)

        title = QLabel("Help")
        title.setObjectName("settingsHelpTitle")
        layout.addWidget(title)

        self._content = QLabel(
            "Wähle eine Kategorie links, um die Einstellungen zu bearbeiten.\n\n"
            "Änderungen werden automatisch gespeichert."
        )
        self._content.setObjectName("settingsPanelDescription")
        self._content.setWordWrap(True)
        self._content.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )
        layout.addWidget(self._content)
        layout.addStretch()

    def set_help_text(self, text: str) -> None:
        """Update help text for current category."""
        self._content.setText(text or "Keine Hilfe verfügbar.")


class SettingsWorkspace(QWidget):
    """
    Full-page settings workspace.

    - Left: Settings categories (SettingsNavigation)
    - Center: Settings content (stacked by category)
    - Right: Help panel (optional)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsWorkspace")
        self._stack_indices: Dict[str, int] = {}
        self._inspector_host = None
        self._setup_ui()
        self._connect_signals()
        self._show_category("settings_application")

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Navigation
        self._nav = SettingsNavigation(self)
        splitter.addWidget(self._nav)

        # Center: Content stack
        self._stack = QStackedWidget()
        self._stack.setObjectName("settingsContentStack")

        for category_id in _category_factories:
            widget = get_category_widget(category_id, self)
            if widget:
                idx = self._stack.addWidget(widget)
                self._stack_indices[category_id] = idx

        splitter.addWidget(self._stack)

        # Right: Help panel (optional)
        self._help_panel = SettingsHelpPanel(self)
        splitter.addWidget(self._help_panel)

        splitter.setSizes([220, 500, 240])
        layout.addWidget(splitter)

    def _connect_signals(self) -> None:
        self._nav.category_selected.connect(self._show_category)

    def _show_category(self, category_id: str) -> None:
        """Show the content for the selected category."""
        if category_id in self._stack_indices:
            self._stack.setCurrentIndex(self._stack_indices[category_id])
            self._nav.set_current(category_id)
            self._update_help(category_id)
            self._update_inspector(category_id)

    def _update_inspector(self, category_id: str) -> None:
        """Set category-specific inspector content."""
        if not self._inspector_host:
            return
        content_token = self._inspector_host.prepare_for_setup()
        widget = self._create_inspector_for_category(category_id)
        if widget:
            self._inspector_host.set_content(widget, content_token=content_token)
        else:
            self._inspector_host.clear_content()

    def _create_inspector_for_category(self, category_id: str) -> Optional[QWidget]:
        """Create inspector widget for category. Returns None to use default placeholder."""
        if category_id == "settings_appearance":
            from app.gui.inspector.appearance_inspector import AppearanceInspector
            from app.gui.themes import get_theme_manager
            theme_id = get_theme_manager().get_current_id()
            return AppearanceInspector(theme_id=theme_id)
        if category_id == "settings_ai_models":
            from app.gui.inspector.models_settings_inspector import ModelsSettingsInspector
            return ModelsSettingsInspector()
        if category_id == "settings_advanced":
            from app.gui.inspector.advanced_settings_inspector import AdvancedSettingsInspector
            return AdvancedSettingsInspector()
        if category_id == "settings_application":
            from app.gui.inspector.system_settings_inspector import SystemSettingsInspector
            return SystemSettingsInspector()
        return None

    def _update_help(self, category_id: str) -> None:
        """Update help panel for category."""
        help_texts = {
            "settings_application": "Anwendungsinformationen und Laufzeitstatus.",
            "settings_appearance": "Theme und Darstellung der Benutzeroberfläche.",
            "settings_ai_models": "Standardmodell, Temperatur und Token-Limits.",
            "settings_data": "Speicherorte, RAG und Prompt-Konfiguration.",
            "settings_privacy": "Datenschutz und API-Keys.",
            "settings_advanced": "Debug-Optionen und experimentelle Features.",
            "settings_project": "Projektspezifische Einstellungen (wenn ein Projekt aktiv ist).",
            "settings_workspace": "Workspace-Einstellungen (Knowledge, Prompt Studio, Agents).",
        }
        self._help_panel.set_help_text(help_texts.get(category_id, ""))

    def show_category(self, category_id: str) -> None:
        """Public API: show a specific category (e.g. from Command Palette)."""
        self._show_category(category_id)

    def get_current_category(self) -> str | None:
        """Returns the currently visible category ID (e.g. settings_appearance)."""
        idx = self._stack.currentIndex()
        for cat_id, stack_idx in self._stack_indices.items():
            if stack_idx == idx:
                return cat_id
        return "settings_application"  # fallback if no match

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Optional: set inspector host for category-specific inspectors. D9: content_token optional."""
        self._inspector_host = inspector_host
        self._update_inspector(self.get_current_category())
