"""
KnowledgeCollectionsPanel – Collections / Knowledge Bases.

Liste der Spaces, Auswahl, Chunk-Anzahl.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
)
from PySide6.QtCore import Signal, Qt
from typing import Optional


def _panel_style() -> str:
    return (
        "background: white; border: 1px solid #e5e7eb; border-radius: 10px; "
        "padding: 12px;"
    )


class KnowledgeCollectionsPanel(QFrame):
    """Collections / Knowledge Bases mit Auswahl."""

    collection_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("knowledgeCollectionsPanel")
        self.setMinimumHeight(180)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Knowledge Bases")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        self._list = QListWidget()
        self._list.setObjectName("collectionsList")
        self._list.setSpacing(2)
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.setStyleSheet(
            "QListWidget { background: #fafafa; border: none; border-radius: 6px; }"
        )
        layout.addWidget(self._list, 1)

    def _on_item_clicked(self, item: QListWidgetItem):
        space = item.data(Qt.ItemDataRole.UserRole)
        if space:
            self.collection_selected.emit(space)

    def refresh(self, project_id: Optional[int] = None) -> None:
        """Lädt Collections aus dem Backend. project_id: bei aktivem Projekt nur Projekt-Space."""
        self._list.clear()
        try:
            from app.services.knowledge_service import get_knowledge_service
            backend = get_knowledge_service()
            spaces = backend.list_spaces(project_id)
            for space in spaces:
                count = backend.get_space_chunk_count(space)
                label = f"{space} ({count} Chunks)"
                if project_id is not None:
                    label = f"Projekt-Space ({count} Chunks)"
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, space)
                self._list.addItem(item)
            if spaces and self._list.count() > 0:
                self._list.setCurrentRow(0)
                self.collection_selected.emit(spaces[0])
        except Exception:
            pass
