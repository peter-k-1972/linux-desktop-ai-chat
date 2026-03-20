"""
NavigationSidebar – Sektionsbasierte Navigation mit einklappbaren Bereichen.

Struktur: PROJECT, WORKSPACE, SYSTEM, OBSERVABILITY, QUALITY, SETTINGS.
Emittiert navigate_requested(area_id, workspace_id).
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QFrame,
    QPushButton,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Signal, Qt

from app.gui.icons import IconManager
from app.gui.navigation.sidebar_config import get_sidebar_sections, NavItem, NavSection


class NavSectionWidget(QFrame):
    """Eine einklappbare Sektion mit Header und Items."""

    item_clicked = Signal(str, object)  # area_id, workspace_id

    def __init__(self, section: NavSection, parent=None):
        super().__init__(parent)
        self.setObjectName("navSection")
        self._section = section
        self._list_widget: QListWidget | None = None
        self._expanded = section.default_expanded
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._header = QPushButton(f"  {self._section.title}")
        self._header.setObjectName("navSectionHeader")
        self._header.setCheckable(False)
        self._header.clicked.connect(self._toggle)
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self._header)

        self._list_widget = QListWidget()
        self._list_widget.setObjectName("navItemList")
        self._list_widget.setSpacing(2)
        self._list_widget.itemClicked.connect(self._on_item_clicked)

        for item in self._section.items:
            list_item = QListWidgetItem(f"  {item.title}")
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            list_item.setIcon(IconManager.get(item.icon, size=18))
            if item.tooltip:
                list_item.setToolTip(item.tooltip)
            self._list_widget.addItem(list_item)

        layout.addWidget(self._list_widget)
        self._update_visibility()  # setzt auch Header-Text mit Pfeil

    def _toggle(self) -> None:
        self._expanded = not self._expanded
        self._update_visibility()

    def _update_visibility(self) -> None:
        self._list_widget.setVisible(self._expanded)
        arrow = "▾" if self._expanded else "▸"
        self._header.setText(f"  {arrow}  {self._section.title}")

    def _on_item_clicked(self, list_item: QListWidgetItem) -> None:
        item: NavItem = list_item.data(Qt.ItemDataRole.UserRole)
        if item:
            self.item_clicked.emit(item.area_id, item.workspace_id)

    def set_current(self, nav_key: str) -> None:
        """Setzt die visuelle Auswahl."""
        for i in range(self._list_widget.count()):
            list_item = self._list_widget.item(i)
            nav_item: NavItem = list_item.data(Qt.ItemDataRole.UserRole)
            if nav_item and nav_item.nav_key == nav_key:
                self._list_widget.blockSignals(True)
                self._list_widget.setCurrentRow(i)
                self._list_widget.blockSignals(False)
                return
        self._list_widget.clearSelection()


class NavigationSidebar(QWidget):
    """Sidebar mit Sektionen. Emittiert navigate_requested(area_id, workspace_id)."""

    navigate_requested = Signal(str, object)  # area_id, workspace_id | None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navigationSidebar")
        self._section_widgets: list[NavSectionWidget] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(2)

        for section in get_sidebar_sections():
            section_widget = NavSectionWidget(section)
            section_widget.item_clicked.connect(self._on_item_clicked)
            self._section_widgets.append(section_widget)
            scroll_layout.addWidget(section_widget)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def _on_item_clicked(self, area_id: str, workspace_id: object) -> None:
        self.navigate_requested.emit(area_id, workspace_id)

    def set_current(self, area_id: str, workspace_id: str | None = None) -> None:
        """Setzt die visuelle Auswahl. Für Kompatibilität mit area_shown."""
        nav_key = workspace_id or area_id
        for section_widget in self._section_widgets:
            section_widget.set_current(nav_key)
