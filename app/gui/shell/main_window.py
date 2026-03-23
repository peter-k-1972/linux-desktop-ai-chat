"""
ShellMainWindow – Schlankes MainWindow für die GUI-Shell.

Nur Docking, Routing, Signal-Vermittlung. Keine Fachlogik.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt

from app.gui.shell.top_bar import TopBar
from app.gui.shell.docking_config import setup_docks
from app.gui.workspace import WorkspaceHost
from app.gui.bootstrap import register_all_screens
from app.gui.navigation.nav_areas import NavArea
from app.gui.commands.bootstrap import register_commands
from app.gui.commands.palette import CommandPaletteDialog
from app.gui.navigation.command_palette import CommandPalette
from app.gui.commands.palette_loader import load_all_palette_commands
from app.gui.breadcrumbs import BreadcrumbManager, BreadcrumbBar, set_breadcrumb_manager


class ShellMainWindow(QMainWindow):
    """
    MainWindow der GUI-Shell.

    Komponiert: TopBar, NavigationSidebar, WorkspaceHost, InspectorHost, BottomPanelHost.
    Leitet navigate_requested(area_id, workspace_id) an WorkspaceHost weiter.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Linux Desktop Chat – Kommandozentrale")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        self._top_bar = TopBar(self)
        self.addToolBar(self._top_bar)

        self._breadcrumb_manager = BreadcrumbManager(self)
        set_breadcrumb_manager(self._breadcrumb_manager)
        self._breadcrumb_bar = BreadcrumbBar(self)
        self._breadcrumb_manager.path_changed.connect(self._breadcrumb_bar.set_path)

        self._workspace_host = WorkspaceHost(self)
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(self._breadcrumb_bar)
        central_layout.addWidget(self._workspace_host, 1)
        self.setCentralWidget(central)

        docks = setup_docks(self)
        self._nav_sidebar = docks["nav_sidebar"]
        self._inspector_host = docks["inspector_host"]
        self._inspector_dock = docks["inspector_dock"]
        self._bottom_host = docks["bottom_host"]

        self._workspace_host.set_inspector_host(self._inspector_host)

        register_all_screens()
        self._workspace_host.register_from_registry()
        self._workspace_host.show_area(NavArea.COMMAND_CENTER)

        register_commands(self._workspace_host)
        load_all_palette_commands(self._workspace_host)
        self._setup_command_palette()

        self._connect_signals()

        self._schedule_tick_controller = None
        self._setup_schedule_ticker()

    def _setup_schedule_ticker(self) -> None:
        from app.gui.scheduling.schedule_tick_controller import ScheduleTickController

        self._schedule_tick_controller = ScheduleTickController(self)
        self._schedule_tick_controller.start()

    def _on_help_requested(self) -> None:
        from app.gui.themes import get_theme_manager
        from app.gui.themes.theme_id_utils import theme_id_to_legacy_light_dark
        from app.help.manual_resolver import show_contextual_help

        mgr = get_theme_manager()
        theme_id = mgr.get_current_id()
        theme = theme_id_to_legacy_light_dark(theme_id)
        show_contextual_help(self._workspace_host, theme=theme, parent=self)

    def _setup_command_palette(self) -> None:
        """Command Palette: Ctrl+K (primary), Ctrl+Shift+P (legacy)."""
        shortcut_k = QShortcut(QKeySequence("Ctrl+K"), self)
        shortcut_k.activated.connect(self._open_command_palette)
        shortcut_p = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        shortcut_p.activated.connect(self._open_command_palette)
        shortcut_f1 = QShortcut(QKeySequence.HelpContents, self)
        shortcut_f1.activated.connect(self._on_help_requested)

    def _open_command_palette(self) -> None:
        """Opens the Command Palette (primary power-user navigation)."""
        palette = CommandPalette(self)
        palette.exec()

    def _open_workspace_graph(self) -> None:
        """Opens the Workspace Graph dialog."""
        from app.gui.navigation.workspace_graph import WorkspaceGraphDialog
        dlg = WorkspaceGraphDialog(self._workspace_host, parent=self)
        dlg.exec()

    def _connect_signals(self):
        """Verbindet Navigation mit WorkspaceHost."""
        self._nav_sidebar.navigate_requested.connect(self._on_nav_requested)
        self._workspace_host.breadcrumb_changed.connect(self._on_breadcrumb_changed)
        self._workspace_host.breadcrumb_changed.connect(self._on_sidebar_selection_changed)
        self._breadcrumb_bar.navigate_requested.connect(self._on_breadcrumb_navigate)
        self._top_bar.command_palette_requested.connect(self._open_command_palette)
        self._top_bar.workspace_graph_requested.connect(self._open_workspace_graph)
        self._top_bar.status_requested.connect(
            lambda: self._workspace_host.show_area(NavArea.RUNTIME_DEBUG)
        )
        self._top_bar.help_requested.connect(self._on_help_requested)
        # D39: Inspector-Dock wieder geöffnet → Inspector für aktuellen Screen aktualisieren
        self._inspector_dock.visibilityChanged.connect(self._on_inspector_dock_visibility_changed)

    def _on_inspector_dock_visibility_changed(self, visible: bool) -> None:
        """D39: Wenn Inspector-Dock sichtbar wird, Inspector-Inhalt aktualisieren."""
        if visible:
            self._workspace_host.refresh_inspector_for_current()

    def _on_nav_requested(self, area_id: str, workspace_id: object) -> None:
        """Navigiert zu Area und optional Workspace."""
        self._workspace_host.show_area(area_id, workspace_id if workspace_id else None)

    def _on_sidebar_selection_changed(self, area_id: str, workspace_id: str) -> None:
        """Aktualisiert die Sidebar-Auswahl bei Navigation."""
        self._nav_sidebar.set_current(area_id, workspace_id or None)

    def _on_breadcrumb_changed(self, area_id: str, workspace_id: str) -> None:
        """Aktualisiert Breadcrumbs."""
        if workspace_id:
            self._breadcrumb_manager.set_workspace(area_id, workspace_id)
        else:
            self._breadcrumb_manager.set_area(area_id)

    def _on_breadcrumb_navigate(self, area_id: str, workspace_id: str) -> None:
        """Navigiert bei Breadcrumb-Klick."""
        self._workspace_host.show_area(area_id, workspace_id or None)

    def closeEvent(self, event) -> None:
        """Shutdown: DB-Commit vor Fensterschließung (Konsistenz mit Legacy)."""
        tick = getattr(self, "_schedule_tick_controller", None)
        if tick is not None:
            tick.stop()
        try:
            from app.services.infrastructure import get_infrastructure
            infra = get_infrastructure()
            if infra and hasattr(infra.database, "commit"):
                infra.database.commit()
        except Exception:
            pass
        super().closeEvent(event)
