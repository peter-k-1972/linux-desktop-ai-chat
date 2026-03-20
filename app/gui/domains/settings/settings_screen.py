"""
SettingsScreen – Full-page Settings Workspace.

Uses SettingsWorkspace (gui/domains/settings) with left nav, center content, right help.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout

from app.gui.shared import BaseScreen
from app.gui.navigation.nav_areas import NavArea


# Map legacy workspace IDs to new category IDs
_WORKSPACE_TO_CATEGORY = {
    "settings_system": "settings_application",
    "settings_appearance": "settings_appearance",
    "settings_models": "settings_ai_models",
    "settings_agents": "settings_advanced",
    "settings_advanced": "settings_advanced",
}


class SettingsScreen(BaseScreen):
    """Settings-Container: Full-page SettingsWorkspace."""

    def __init__(self, parent=None):
        super().__init__(NavArea.SETTINGS, parent)
        self._inspector_host = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        from app.gui.domains.settings.settings_workspace import SettingsWorkspace
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._workspace = SettingsWorkspace(self)
        layout.addWidget(self._workspace)

    def show_workspace(self, workspace_id: str) -> None:
        """Shows a settings category. Maps legacy IDs to new category IDs."""
        category_id = _WORKSPACE_TO_CATEGORY.get(workspace_id, workspace_id)
        self._workspace.show_category(category_id)
        try:
            from app.gui.breadcrumbs import get_breadcrumb_manager
            mgr = get_breadcrumb_manager()
            if mgr:
                mgr.set_workspace(self.area_id, workspace_id)
        except Exception:
            pass

    def get_current_workspace(self) -> str | None:
        """For Breadcrumbs compatibility. Returns the currently visible category."""
        return self._workspace.get_current_category()

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Delegates to SettingsWorkspace. D9: content_token optional (Settings uses clear_content)."""
        self._inspector_host = inspector_host
        self._workspace.setup_inspector(inspector_host, content_token=content_token)
