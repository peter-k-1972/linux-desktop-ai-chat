"""
KnowledgeNavigationPanel – Left sidebar for Knowledge workspace.

Navigation items: Sources, Collections, Index, Settings.
Emits section_selected(section_id) when a section is clicked.
"""

from typing import List, Tuple

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


# section_id -> (title, icon_name)
# Settings removed from nav until implemented (was placeholder)
KNOWLEDGE_SECTIONS: List[Tuple[str, str, str]] = [
    ("knowledge_sources", "Sources", IconRegistry.DATA_STORES),
    ("knowledge_collections", "Collections", IconRegistry.KNOWLEDGE),
    ("knowledge_index", "Index", IconRegistry.SEARCH),
]


class KnowledgeNavigationPanel(QFrame):
    """
    Left navigation for Knowledge workspace sections.

    Emits section_selected(section_id) when a section is clicked.
    """

    section_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("knowledgeNavigationPanel")
        self.setMinimumWidth(200)
        self.setMaximumWidth(260)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(8)

        title = QLabel("Knowledge")
        title.setObjectName("knowledgeNavTitle")
        title.setStyleSheet("""
            #knowledgeNavTitle {
                font-size: 18px;
                font-weight: 600;
                color: #0f172a;
            }
        """)
        layout.addWidget(title)

        subtitle = QLabel("Wissensräume")
        subtitle.setObjectName("knowledgeNavSubtitle")
        subtitle.setStyleSheet("font-size: 12px; color: #64748b;")
        layout.addWidget(subtitle)

        self._list = QListWidget()
        self._list.setObjectName("knowledgeNavList")
        self._list.setSpacing(2)
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.setStyleSheet("""
            #knowledgeNavList {
                background: transparent;
                border: none;
            }
            #knowledgeNavList::item {
                padding: 10px 14px;
                border-radius: 8px;
            }
            #knowledgeNavList::item:hover {
                background: #f1f5f9;
            }
            #knowledgeNavList::item:selected {
                background: #e2e8f0;
                color: #0f172a;
            }
        """)
        layout.addWidget(self._list, 1)

        self.setStyleSheet("""
            #knowledgeNavigationPanel {
                background: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }
        """)

        self._populate()

    def _populate(self) -> None:
        """Populate list from sections."""
        self._list.clear()
        for section_id, title, icon_name in KNOWLEDGE_SECTIONS:
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, section_id)
            icon = IconManager.get(icon_name, size=18)
            if icon:
                item.setIcon(icon)
            self._list.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        section_id = item.data(Qt.ItemDataRole.UserRole)
        if section_id:
            self.section_selected.emit(section_id)

    def set_current(self, section_id: str) -> None:
        """Set the currently selected section."""
        for i in range(self._list.count()):
            if self._list.item(i).data(Qt.ItemDataRole.UserRole) == section_id:
                self._list.setCurrentRow(i)
                return
        self._list.clearSelection()
