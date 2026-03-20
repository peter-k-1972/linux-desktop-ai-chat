"""Workspace settings category – workspace-scoped settings placeholder."""

from PySide6.QtWidgets import QVBoxLayout

from app.gui.icons.registry import IconRegistry
from app.gui.shared import apply_settings_layout
from app.gui.domains.settings.categories.base_category import BaseSettingsCategory
from app.gui.widgets import EmptyStateWidget


class WorkspaceCategory(BaseSettingsCategory):
    """Workspace settings: per-workspace configuration. Empty state until implemented."""

    def __init__(self, parent=None):
        super().__init__("settings_workspace", parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        apply_settings_layout(layout)

        empty = EmptyStateWidget(
            title="Workspace-spezifische Einstellungen",
            description="Dieser Bereich wird in einer zukünftigen Version erweitert.",
            icon=IconRegistry.GEAR,
            parent=self,
        )
        layout.addWidget(empty)
        layout.addStretch()
