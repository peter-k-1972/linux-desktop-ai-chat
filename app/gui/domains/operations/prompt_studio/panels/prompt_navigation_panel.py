"""
PromptNavigationPanel – Left navigation for Prompt Studio.

Sections: Prompts, Templates, Test Lab, Settings.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
)
from PySide6.QtCore import Qt, Signal

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


# Section IDs for Prompt Studio navigation
# Settings removed from nav until implemented (was placeholder)
SECTION_PROMPTS = "prompts"
SECTION_TEMPLATES = "templates"
SECTION_TEST_LAB = "test_lab"

# (section_id, title, icon_name)
PROMPT_STUDIO_SECTIONS = [
    (SECTION_PROMPTS, "Prompts", IconRegistry.PROMPT_STUDIO),
    (SECTION_TEMPLATES, "Templates", IconRegistry.EDIT),
    (SECTION_TEST_LAB, "Test Lab", IconRegistry.REPLAY_LAB),
]


class PromptNavigationPanel(QFrame):
    """
    Left navigation panel for Prompt Studio.

    Sections: Prompts, Templates, Test Lab, Settings.
    Emits section_selected(section_id) when a section is clicked.
    """

    section_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("promptNavigationPanel")
        self.setMinimumWidth(200)
        self.setMaximumWidth(280)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(8)

        title = QLabel("Prompt Studio")
        title.setObjectName("promptNavTitle")
        title.setStyleSheet("""
            #promptNavTitle {
                font-size: 18px;
                font-weight: 600;
                color: #0f172a;
            }
        """)
        layout.addWidget(title)

        subtitle = QLabel("Navigation")
        subtitle.setObjectName("promptNavSubtitle")
        subtitle.setStyleSheet("font-size: 12px; color: #64748b;")
        layout.addWidget(subtitle)

        self._list = QListWidget()
        self._list.setObjectName("promptNavList")
        self._list.setSpacing(2)
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.setStyleSheet("""
            #promptNavList {
                background: transparent;
                border: none;
            }
            #promptNavList::item {
                padding: 10px 14px;
                border-radius: 8px;
            }
            #promptNavList::item:hover {
                background: #f1f5f9;
            }
            #promptNavList::item:selected {
                background: #e2e8f0;
                color: #0f172a;
            }
        """)
        layout.addWidget(self._list, 1)

        self.setStyleSheet("""
            #promptNavigationPanel {
                background: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }
        """)

        self._populate()

    def _populate(self) -> None:
        """Populate list with sections."""
        self._list.clear()
        for section_id, title, icon_name in PROMPT_STUDIO_SECTIONS:
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
