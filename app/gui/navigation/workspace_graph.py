"""
Workspace Graph Navigator – visual map of workspaces and areas.

Provides a clickable, grouped map for orientation and navigation.
Integrates: sidebar config, help topics, feature registry, trace map.
"""

from typing import Callable, Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QLabel,
    QWidget,
    QGridLayout,
    QPushButton,
    QSplitter,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

from app.gui.navigation.sidebar_config import get_sidebar_sections, NavItem, NavSection
from app.gui.icons import IconManager
from app.gui.breadcrumbs.manager import WORKSPACE_INFO, AREA_TITLES
from app.gui.navigation.workspace_graph_resolver import resolve_metadata, WorkspaceNodeMetadata


def _get_description(item: NavItem) -> str:
    """Short description for tooltip: NavItem.tooltip or WORKSPACE_INFO title."""
    if item.tooltip:
        return item.tooltip
    if item.workspace_id:
        info = WORKSPACE_INFO.get(item.workspace_id)
        if info:
            return info[1]
    return item.title




class WorkspaceGraphNode(QPushButton):
    """Clickable node for a workspace or area."""

    def __init__(
        self,
        item: NavItem,
        is_active: bool,
        on_click: Callable[[str, Optional[str]], None],
        on_hover: Callable[[Optional[NavItem]], None],
        parent=None,
    ):
        super().__init__(parent)
        self._item = item
        self._on_click = on_click
        self._on_hover = on_hover
        self._is_active = is_active
        self.setObjectName("workspaceGraphNode")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setCheckable(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._build_ui()
        self.clicked.connect(self._handle_click)

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        if self._item.icon:
            icon = IconManager.get(self._item.icon, size=20)
            if not icon.isNull():
                icon_label = QLabel()
                icon_label.setPixmap(icon.pixmap(20, 20))
                layout.addWidget(icon_label)
        label = QLabel(self._item.title)
        label.setObjectName("workspaceGraphNodeLabel")
        layout.addWidget(label)
        self.setToolTip(_get_description(self._item))
        self._apply_style()

    def enterEvent(self, event):
        super().enterEvent(event)
        self._on_hover(self._item)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._on_hover(None)

    def _handle_click(self) -> None:
        self._on_click(self._item.area_id, self._item.workspace_id)

    def _apply_style(self) -> None:
        try:
            from app.gui.themes import get_theme_manager
            tokens = get_theme_manager().get_tokens()
            bg = tokens.get("color_bg_surface", "#ffffff")
            border = tokens.get("color_border", "#e2e8f0")
            text = tokens.get("color_text", "#1f2937")
            active_bg = tokens.get("color_bg_selected", "#dbeafe")
            hover_bg = tokens.get("color_bg_hover", "#f3f4f6")
            if self._is_active:
                self.setStyleSheet(f"""
                    #workspaceGraphNode {{
                        background: {active_bg};
                        border: 2px solid {tokens.get('color_accent', '#3b82f6')};
                        border-radius: 8px;
                        padding: 4px;
                    }}
                    #workspaceGraphNodeLabel {{ color: {text}; font-weight: 600; }}
                """)
            else:
                self.setStyleSheet(f"""
                    #workspaceGraphNode {{
                        background: {bg};
                        border: 1px solid {border};
                        border-radius: 8px;
                        padding: 4px;
                    }}
                    #workspaceGraphNode:hover {{
                        background: {hover_bg};
                    }}
                    #workspaceGraphNodeLabel {{ color: {text}; }}
                """)
        except Exception:
            self.setStyleSheet("""
                #workspaceGraphNode {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                }
                #workspaceGraphNode:hover { background: #f1f5f9; }
            """)


class WorkspaceGraphDetailsPanel(QFrame):
    """Side panel showing metadata for the hovered/selected workspace node."""

    def __init__(self, workspace_host, on_navigate: Callable[[str, Optional[str]], None], parent=None):
        super().__init__(parent)
        self._workspace_host = workspace_host
        self._on_navigate = on_navigate
        self._current_item: Optional[NavItem] = None
        self.setObjectName("workspaceGraphDetailsPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(360)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self._placeholder = QLabel("Hover over a workspace to see details")
        self._placeholder.setObjectName("detailsPlaceholder")
        self._placeholder.setWordWrap(True)
        layout.addWidget(self._placeholder)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)
        self._content.hide()
        layout.addWidget(self._content)

        self._title_label = QLabel()
        self._title_label.setObjectName("detailsTitle")
        self._area_label = QLabel()
        self._desc_label = QLabel()
        self._desc_label.setWordWrap(True)
        self._help_label = QLabel()
        self._help_label.setWordWrap(True)
        self._features_label = QLabel()
        self._features_label.setWordWrap(True)
        self._code_label = QLabel()
        self._code_label.setWordWrap(True)
        self._related_label = QLabel()
        self._related_label.setWordWrap(True)

        self._btn_open_workspace = QPushButton("Open Workspace")
        self._btn_open_workspace.setObjectName("detailsOpenWorkspace")
        self._btn_open_help = QPushButton("Open Help")
        self._btn_open_help.setObjectName("detailsOpenHelp")

        self._content_layout.addWidget(self._title_label)
        self._content_layout.addWidget(self._area_label)
        self._content_layout.addWidget(self._desc_label)
        self._content_layout.addWidget(self._btn_open_workspace)
        self._content_layout.addWidget(self._btn_open_help)
        self._content_layout.addWidget(self._help_label)
        self._content_layout.addWidget(self._features_label)
        self._content_layout.addWidget(self._code_label)
        self._content_layout.addWidget(self._related_label)
        self._content_layout.addStretch()

        self._btn_open_workspace.clicked.connect(self._do_open_workspace)
        self._btn_open_help.clicked.connect(self._do_open_help)

    def set_item(self, item: Optional[NavItem]) -> None:
        """Update panel for hovered/selected item."""
        self._current_item = item
        if not item:
            self._placeholder.show()
            self._content.hide()
            return

        self._placeholder.hide()
        self._content.show()

        meta = resolve_metadata(
            item.workspace_id,
            item.area_id,
            item.title,
            item.tooltip or "",
        )

        self._title_label.setText(meta.title)
        area_title = AREA_TITLES.get(meta.area_id, meta.area_id.replace("_", " ").title())
        self._area_label.setText(f"Area: {area_title}")

        desc = meta.short_description or meta.title
        self._desc_label.setText(desc)

        # Help
        if meta.help_topic_id and meta.help_topic_title:
            self._help_label.setText(f"Help: {meta.help_topic_title}")
            self._help_label.setVisible(True)
            self._btn_open_help.setVisible(True)
        else:
            self._help_label.setText("No help article mapped")
            self._help_label.setVisible(True)
            self._btn_open_help.setVisible(False)

        # Features
        if meta.feature_names:
            self._features_label.setText("Features: " + ", ".join(meta.feature_names))
            self._features_label.setVisible(True)
        else:
            self._features_label.setVisible(False)

        # Code paths
        if meta.code_module_paths:
            paths = meta.code_module_paths[:3]
            text = "Code: " + ", ".join(paths)
            if len(meta.code_module_paths) > 3:
                text += f" (+{len(meta.code_module_paths) - 3} more)"
            self._code_label.setText(text)
            self._code_label.setVisible(True)
        else:
            self._code_label.setVisible(False)

        # Related
        if meta.related_workspace_ids:
            from app.gui.breadcrumbs.manager import WORKSPACE_INFO
            related_titles = []
            for rid in meta.related_workspace_ids[:5]:
                info = WORKSPACE_INFO.get(rid)
                related_titles.append(info[1] if info else rid)
            self._related_label.setText("See also: " + ", ".join(related_titles))
            self._related_label.setVisible(True)
        else:
            self._related_label.setVisible(False)

    def _do_open_workspace(self) -> None:
        if self._current_item:
            self._on_navigate(self._current_item.area_id, self._current_item.workspace_id)

    def _do_open_help(self) -> None:
        if not self._current_item:
            return
        meta = resolve_metadata(
            self._current_item.workspace_id,
            self._current_item.area_id,
            self._current_item.title,
            self._current_item.tooltip or "",
        )
        if not meta.help_topic_id:
            return
        try:
            from PySide6.QtWidgets import QApplication
            from app.gui.themes import get_theme_manager
            from app.help.help_window import HelpWindow
            mgr = get_theme_manager()
            theme_id = mgr.get_current_id()
            theme = "dark" if "dark" in (theme_id or "") else "light"
            parent = QApplication.activeWindow()
            win = HelpWindow(theme=theme, parent=parent, initial_topic_id=meta.help_topic_id)
            win.exec()
        except Exception:
            pass


class WorkspaceGraphDialog(QDialog):
    """
    Dialog showing the Workspace Graph – grouped map of areas and workspaces.

    - Uses get_sidebar_sections() as data source
    - Details panel shows metadata (help, features, code paths, related)
    - Click navigates via callback (workspace_host.show_area)
    - Highlights current workspace
    """

    def __init__(
        self,
        workspace_host,
        parent=None,
    ):
        super().__init__(parent)
        self._workspace_host = workspace_host
        self.setWindowTitle("Workspace Graph – System Map")
        self.setObjectName("workspaceGraphDialog")
        self.setMinimumSize(720, 500)
        self.resize(960, 600)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        title = QLabel("Workspace Graph")
        title.setObjectName("workspaceGraphTitle")
        layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: graph content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(24)
        content_layout.setContentsMargins(0, 0, 0, 0)

        current_key = self._workspace_host.get_current_workspace_id()
        sections = get_sidebar_sections()

        self._details_panel = WorkspaceGraphDetailsPanel(
            self._workspace_host,
            on_navigate=self._on_navigate,
        )

        for section in sections:
            section_widget = self._build_section(section, current_key)
            content_layout.addWidget(section_widget)

        content_layout.addStretch()
        scroll.setWidget(content)
        splitter.addWidget(scroll)

        # Right: details panel
        splitter.addWidget(self._details_panel)
        splitter.setSizes([600, 300])

        layout.addWidget(splitter, 1)

        self._apply_theme()

    def _apply_theme(self) -> None:
        try:
            from app.gui.themes import get_theme_manager
            tokens = get_theme_manager().get_tokens()
            bg = tokens.get("color_bg", "#ffffff")
            text = tokens.get("color_text", "#1f2937")
            muted = tokens.get("color_text_muted", "#6b7280")
            border = tokens.get("color_border", "#e2e8f0")
            surface = tokens.get("color_bg_surface", "#f8fafc")
            self.setStyleSheet(f"""
                #workspaceGraphDialog {{ background: {bg}; }}
                #workspaceGraphTitle {{
                    font-size: 18px;
                    font-weight: 600;
                    color: {text};
                }}
                #workspaceGraphSectionHeader {{
                    font-size: 12px;
                    font-weight: 600;
                    color: {muted};
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                #workspaceGraphDetailsPanel {{
                    background: {surface};
                    border: 1px solid {border};
                    border-radius: 8px;
                }}
                #detailsPlaceholder {{ color: {muted}; font-size: 13px; }}
                #detailsTitle {{ font-size: 15px; font-weight: 600; color: {text}; }}
                #detailsOpenWorkspace, #detailsOpenHelp {{
                    padding: 8px 12px;
                    border-radius: 6px;
                }}
            """)
        except Exception:
            pass

    def _build_section(self, section: NavSection, current_key: str) -> QWidget:
        frame = QFrame()
        frame.setObjectName("workspaceGraphSection")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(8)

        header = QLabel(section.title)
        header.setObjectName("workspaceGraphSectionHeader")
        layout.addWidget(header)

        grid = QGridLayout()
        grid.setSpacing(8)
        row, col = 0, 0
        max_cols = 4
        for item in section.items:
            is_active = item.nav_key == current_key
            node = WorkspaceGraphNode(
                item,
                is_active=is_active,
                on_click=self._on_node_click,
                on_hover=self._details_panel.set_item,
            )
            grid.addWidget(node, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        layout.addLayout(grid)
        return frame

    def _on_node_click(self, area_id: str, workspace_id: Optional[str]) -> None:
        """Navigate and close dialog."""
        self._workspace_host.show_area(area_id, workspace_id)
        self.accept()

    def _on_navigate(self, area_id: str, workspace_id: Optional[str]) -> None:
        """Navigate (from details panel) and close."""
        self._workspace_host.show_area(area_id, workspace_id)
        self.accept()
