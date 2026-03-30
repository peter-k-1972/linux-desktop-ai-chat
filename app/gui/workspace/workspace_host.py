"""
WorkspaceHost – Zentraler Container für Screens.

Verwendet QStackedWidget. Zeigt je nach area_id den entsprechenden Screen.
Nutzt ScreenRegistry – keine If/Else-Ketten.
Unterstützt Inspector-Integration via setup_inspector.
"""

from PySide6.QtWidgets import QStackedWidget, QWidget
from PySide6.QtCore import Signal
from app.gui.workspace.screen_registry import get_screen_registry


class WorkspaceHost(QStackedWidget):
    """Stack-basierter Host für Workspace-Screens."""

    area_shown = Signal(str)
    breadcrumb_changed = Signal(str, str)  # area_id, workspace_id ("" wenn nur Area)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("workspaceHost")
        self._screens: dict[str, QWidget] = {}
        self._area_to_index: dict[str, int] = {}
        self._inspector_host = None
        self._current_area_id = ""
        self._current_workspace_id = ""
        self.currentChanged.connect(self._on_current_changed)

    def set_inspector_host(self, inspector_host) -> None:
        """Setzt den InspectorHost für kontextabhängige Inhalte."""
        self._inspector_host = inspector_host

    def register_from_registry(self) -> None:
        """Lädt alle Screens aus der ScreenRegistry und registriert ihre Factories als konkrete Screen-Instanzen."""
        registry = get_screen_registry()
        for area_id in registry.list_areas():
            screen = registry.create_screen(area_id)
            if screen:
                self.register_screen(area_id, screen)

    def register_screen(self, area_id: str, screen: QWidget) -> None:
        """Registriert einen Screen für eine area_id."""
        if area_id in self._screens:
            return
        index = self.addWidget(screen)
        self._screens[area_id] = screen
        self._area_to_index[area_id] = index

    def show_area(self, area_id: str, workspace_id: str | None = None) -> None:
        """Zeigt den Screen für die angegebene area_id. Optional: workspace_id für Sub-Workspace."""
        if area_id in self._area_to_index:
            self.setCurrentIndex(self._area_to_index[area_id])
            widget = self.widget(self._area_to_index[area_id])
            bc_workspace = ""
            if workspace_id and widget and hasattr(widget, "show_workspace"):
                widget.show_workspace(workspace_id)
                bc_workspace = workspace_id
            elif widget and hasattr(widget, "get_current_workspace"):
                ws = widget.get_current_workspace()
                if ws:
                    bc_workspace = ws
            self._current_area_id = area_id
            self._current_workspace_id = bc_workspace or ""
            self.area_shown.emit(area_id)
            self.breadcrumb_changed.emit(area_id, bc_workspace)

    def get_current_workspace_id(self) -> str:
        """Aktueller workspace_id für Kontexthilfe (z.B. operations_chat, cc_models)."""
        return self._current_workspace_id or self._current_area_id

    def _on_current_changed(self, index: int) -> None:
        """Aktualisiert den Inspector bei Screen-Wechsel. D24: Token verhindert stale Updates. D39: Skip wenn Inspector unsichtbar."""
        if not self._inspector_host:
            return
        if not self._inspector_host.isVisible():
            return
        content_token = self._inspector_host.prepare_for_setup()
        widget = self.widget(index)
        if widget and hasattr(widget, "setup_inspector"):
            widget.setup_inspector(self._inspector_host, content_token=content_token)
        else:
            self._inspector_host.clear_content()

    def refresh_inspector_for_current(self) -> None:
        """D39: Aktualisiert den Inspector für den aktuellen Screen (z.B. wenn Inspector-Dock wieder geöffnet wird)."""
        self._on_current_changed(self.currentIndex())
