"""
Workbench shell: QMainWindow with central tab canvas and docked explorer, inspector, console.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDockWidget,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from app.gui.shell.layout_constants import (
    BOTTOM_PANEL_HEIGHT,
    INSPECTOR_WIDTH,
    NAV_SIDEBAR_WIDTH,
)
from app.gui.workbench.canvas.canvas_router import CanvasRouter
from app.gui.workbench.canvas.canvas_tabs import CanvasTabs
from app.gui.workbench.command_palette.command_context import WorkbenchCommandContext
from app.gui.workbench.command_palette.command_palette_dialog import CommandPaletteDialog
from app.gui.workbench.command_palette.command_registry import WorkbenchCommandRegistry
from app.gui.workbench.command_palette.workbench_commands import register_workbench_commands
from app.gui.workbench.console.console_panel import ConsolePanel
from app.gui.workbench.explorer.explorer_panel import ExplorerPanel
from app.gui.workbench.focus.active_object import ActiveObject
from app.gui.workbench.focus.contextual_actions import contextual_action_tuples
from app.gui.workbench.focus.workbench_focus_controller import WorkbenchFocusController
from app.gui.workbench.inspector.inspector_panel import InspectorPanel
from app.gui.workbench.ui.context_action_bar import ContextActionBar
from app.gui.workbench.workbench_controller import WorkbenchController


class MainWorkbench(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchMainWindow")
        self.setWindowTitle("Linux Desktop Chat – Workbench")
        self.setMinimumSize(1000, 700)
        self.resize(1280, 820)

        self._canvas_tabs = CanvasTabs(self)
        self._focus_controller = WorkbenchFocusController(self)

        _central = QWidget(self)
        _central_lay = QVBoxLayout(_central)
        _central_lay.setContentsMargins(0, 0, 0, 0)
        _central_lay.setSpacing(0)
        self._context_action_bar = ContextActionBar(self, _central)
        _central_lay.addWidget(self._context_action_bar)
        _central_lay.addWidget(self._canvas_tabs, 1)
        self.setCentralWidget(_central)

        self._focus_controller.active_object_changed.connect(self._on_active_object_changed)

        self._explorer_panel = ExplorerPanel(self)
        self._explorer_dock = QDockWidget("Explorer", self)
        self._explorer_dock.setObjectName("workbenchExplorerDock")
        self._explorer_dock.setWidget(self._explorer_panel)
        self._explorer_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self._explorer_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._explorer_dock)
        self._explorer_dock.setMinimumWidth(NAV_SIDEBAR_WIDTH)

        self._inspector_panel = InspectorPanel(self)
        self._inspector_dock = QDockWidget("Inspector", self)
        self._inspector_dock.setObjectName("workbenchInspectorDock")
        self._inspector_dock.setWidget(self._inspector_panel)
        self._inspector_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self._inspector_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._inspector_dock)
        self._inspector_dock.setMinimumWidth(INSPECTOR_WIDTH)

        self._console_panel = ConsolePanel(self)
        self._console_dock = QDockWidget("Console", self)
        self._console_dock.setObjectName("workbenchConsoleDock")
        self._console_dock.setWidget(self._console_panel)
        self._console_dock.setAllowedAreas(
            Qt.DockWidgetArea.TopDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea
        )
        self._console_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._console_dock)
        self._console_dock.setMinimumHeight(BOTTOM_PANEL_HEIGHT)

        self._command_registry = WorkbenchCommandRegistry()
        register_workbench_commands(self._command_registry)

        self._controller = WorkbenchController(self)
        self._build_menu_and_toolbar()
        self._setup_workbench_shortcuts()

    def _on_active_object_changed(self, active: object) -> None:
        if not isinstance(active, ActiveObject):
            return
        self._context_action_bar.sync_from_focus(active)
        self._inspector_panel.set_focus_context(active)
        if active.tab_key:
            self._canvas_tabs.set_tab_status(active.tab_key, active.status)

    @property
    def focus_controller(self) -> WorkbenchFocusController:
        return self._focus_controller

    def set_active_object(self, object_type: str, object_id: str | None) -> None:
        """Set global active object (normally the tab strip does this)."""
        self._focus_controller.set_active_object(object_type, object_id)

    @property
    def canvas_tabs(self) -> CanvasTabs:
        return self._canvas_tabs

    @property
    def explorer_panel(self) -> ExplorerPanel:
        return self._explorer_panel

    @property
    def inspector_panel(self) -> InspectorPanel:
        return self._inspector_panel

    @property
    def console_panel(self) -> ConsolePanel:
        return self._console_panel

    @property
    def canvas_router(self) -> CanvasRouter:
        return self._controller.canvas_router

    def open_command_palette(self) -> None:
        ctx = WorkbenchCommandContext(
            window=self,
            active_canvas=self.canvas_tabs.current_canvas(),
            active_object=self.focus_controller.active_object,
        )
        CommandPaletteDialog(self._command_registry, ctx, self).exec()

    def focus_console(self) -> None:
        self._console_dock.show()
        self._console_dock.raise_()
        self._console_panel.setFocus(Qt.FocusReason.OtherFocusReason)

    def toggle_inspector(self) -> None:
        self._inspector_dock.setVisible(not self._inspector_dock.isVisible())

    def toggle_console(self) -> None:
        self._console_dock.setVisible(not self._console_dock.isVisible())

    def _setup_workbench_shortcuts(self) -> None:
        pal = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        pal.setContext(Qt.ShortcutContext.WindowShortcut)
        pal.activated.connect(self.open_command_palette)
        run_sc = QShortcut(QKeySequence(Qt.Key.Key_F5), self)
        run_sc.setContext(Qt.ShortcutContext.WindowShortcut)
        run_sc.activated.connect(self._trigger_primary_context_action)

    def _trigger_primary_context_action(self) -> None:
        acts = contextual_action_tuples(self, self.focus_controller.active_object)
        if acts:
            acts[0][1]()

    def _build_menu_and_toolbar(self) -> None:
        menu_bar = QMenuBar(self)
        menu_bar.setObjectName("workbenchMenuBar")
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&File")
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        wf_menu = menu_bar.addMenu("&Workflows")
        wf_menu.addAction(self._workflow_action("Test Agent…", lambda: self.canvas_router.open_agent_test()))
        wf_menu.addAction(self._workflow_action("Create Knowledge Base…", self._workflow_create_kb))
        wf_menu.addAction(self._workflow_action("Build Workflow", lambda: self.canvas_router.open_workflow_builder()))
        wf_menu.addAction(self._workflow_action("Develop Prompt", lambda: self.canvas_router.open_prompt_development()))
        wf_menu.addAction(self._workflow_action("Compare Models", lambda: self.canvas_router.open_model_compare()))

        view_menu = menu_bar.addMenu("&View")
        palette_act = QAction("Command Palette…", self)
        palette_act.triggered.connect(self.open_command_palette)
        view_menu.addAction(palette_act)
        view_menu.addSeparator()
        for dock, label in (
            (self._explorer_dock, "Explorer"),
            (self._inspector_dock, "Inspector"),
            (self._console_dock, "Console"),
        ):
            toggle = dock.toggleViewAction()
            toggle.setText(label)
            view_menu.addAction(toggle)

        help_menu = menu_bar.addMenu("&Help")
        about = QAction("About Workbench…", self)
        about.triggered.connect(self._on_about)
        help_menu.addAction(about)

        toolbar = QToolBar("Workbench", self)
        toolbar.setObjectName("workbenchToolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(toolbar.iconSize())
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        primary = QPushButton("Commands")
        primary.setObjectName("workbenchToolbarPrimaryButton")
        primary.setToolTip("Command Palette (Ctrl+Shift+P)")
        primary.setCursor(Qt.CursorShape.PointingHandCursor)
        primary.clicked.connect(self.open_command_palette)
        act_primary = QWidgetAction(self)
        act_primary.setDefaultWidget(primary)
        toolbar.addAction(act_primary)

        toolbar.addSeparator()

        wf_btn = QToolButton(self)
        wf_btn.setText("Workflows")
        wf_btn.setToolTip("Task-oriented workflows")
        wf_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        wf_tb_menu = QMenu(wf_btn)
        wf_tb_menu.addAction(self._workflow_action("Test Agent", lambda: self.canvas_router.open_agent_test()))
        wf_tb_menu.addAction(self._workflow_action("Knowledge Base", self._workflow_create_kb))
        wf_tb_menu.addAction(self._workflow_action("Build Workflow", lambda: self.canvas_router.open_workflow_builder()))
        wf_tb_menu.addAction(self._workflow_action("Develop Prompt", lambda: self.canvas_router.open_prompt_development()))
        wf_tb_menu.addAction(self._workflow_action("Compare Models", lambda: self.canvas_router.open_model_compare()))
        wf_btn.setMenu(wf_tb_menu)
        toolbar.addWidget(wf_btn)

        toolbar.addSeparator()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        badge = QLabel("AI Workbench")
        badge.setObjectName("workbenchModeBadge")
        toolbar.addWidget(badge)

        toolbar.addSeparator()
        toolbar.addAction(quit_action)

    def _on_about(self) -> None:
        self._console_panel.log_output("Workbench — use Explorer, canvas tabs, and Ctrl+Shift+P.")

    def _workflow_action(self, text: str, fn) -> QAction:
        act = QAction(text, self)
        act.triggered.connect(lambda *_: fn())
        return act

    def _workflow_create_kb(self) -> None:
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "Knowledge base", "Name:")
        if not ok:
            return
        label = name.strip() or "New knowledge base"
        slug = label.lower().replace(" ", "-")[:48] or "new-kb"
        self.canvas_router.open_knowledge_base_workflow(kb_id=slug, display_name=label)
