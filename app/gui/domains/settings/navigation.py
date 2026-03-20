"""
SettingsNavigation – Left sidebar with settings categories.

Extendable: categories are registered via SettingsCategoryRegistry.
"""

from typing import Callable, Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt, Signal

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


# Category ID -> (title, icon_name)
# Structure: Application (first 6) | Project | Workspace
DEFAULT_CATEGORIES: List[Tuple[str, str, str]] = [
    # Application Settings (global)
    ("settings_application", "Application", IconRegistry.SYSTEM),
    ("settings_appearance", "Appearance", IconRegistry.APPEARANCE),
    ("settings_ai_models", "AI / Models", IconRegistry.MODELS),
    ("settings_data", "Data", IconRegistry.DATA_STORES),
    ("settings_privacy", "Privacy", IconRegistry.SHIELD),
    ("settings_advanced", "Advanced", IconRegistry.ADVANCED),
    # Project Settings (project-scoped)
    ("settings_project", "Project", IconRegistry.PROJECTS),
    # Workspace Settings (workspace-scoped)
    ("settings_workspace", "Workspace", IconRegistry.GEAR),
]

# Extendable registry: category_id -> (title, icon_name)
_category_registry: Dict[str, Tuple[str, str]] = {
    cid: (title, icon) for cid, title, icon in DEFAULT_CATEGORIES
}


def register_settings_category(category_id: str, title: str, icon_name: str = IconRegistry.GEAR) -> None:
    """Register a settings category. Extendable API."""
    _category_registry[category_id] = (title, icon_name)


def get_settings_categories() -> List[Tuple[str, str, str]]:
    """Return all registered categories as (id, title, icon_name)."""
    return [(cid, title, icon) for cid, (title, icon) in _category_registry.items()]


class SettingsNavigation(QFrame):
    """
    Left navigation for settings categories.

    Emits category_selected(category_id) when a category is clicked.
    """

    category_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsNavigation")
        self.setMinimumWidth(200)
        self.setMaximumWidth(260)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(8)

        title = QLabel("Settings")
        title.setObjectName("settingsNavTitle")
        layout.addWidget(title)

        subtitle = QLabel("Einstellungen")
        subtitle.setObjectName("settingsNavSubtitle")
        layout.addWidget(subtitle)

        self._list = QListWidget()
        self._list.setObjectName("settingsNavList")
        self._list.setSpacing(2)
        self._list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._list, 1)

        self._populate()

    def _populate(self) -> None:
        """Populate list from registry."""
        self._list.clear()
        for category_id, title, icon_name in get_settings_categories():
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, category_id)
            icon = IconManager.get(icon_name, size=18)
            if icon:
                item.setIcon(icon)
            self._list.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        category_id = item.data(Qt.ItemDataRole.UserRole)
        if category_id:
            self.category_selected.emit(category_id)

    def set_current(self, category_id: str) -> None:
        """Set the currently selected category."""
        for i in range(self._list.count()):
            if self._list.item(i).data(Qt.ItemDataRole.UserRole) == category_id:
                self._list.setCurrentRow(i)
                return
        self._list.clearSelection()
