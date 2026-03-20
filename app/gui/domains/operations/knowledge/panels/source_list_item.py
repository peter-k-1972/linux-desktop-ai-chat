"""
SourceListItemWidget – Single source entry in the Knowledge Sources list.

Canonical implementation. Displays: name, type, status, optional chunk_count, collection.
Context menu: Delete, Reindex.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QMenu
from PySide6.QtCore import Qt

STATUS_LABELS = {
    "indexiert": "indexiert",
    "registriert": "registriert",
    "fehlerhaft": "fehlerhaft",
    "in Bearbeitung": "in Bearbeitung",
    "neu": "neu",
}

TYPE_LABELS = {
    "datei": "Datei",
    "ordner": "Ordner",
    "file": "File",
    "folder": "Folder",
    "url": "URL",
    "note": "Note",
    "quelle": "Quelle",
}


def _format_chunk_count(count: int | None) -> str:
    """Format chunk count for display."""
    if count is None:
        return "—"
    if count == 0:
        return "0 chunks"
    return f"{count} chunks"


class SourceListItemWidget(QFrame):
    """
    Clickable source item: name, type, status, optional chunk_count, collection.
    Context menu: Delete, Reindex.
    """

    def __init__(
        self,
        path: str,
        name: str,
        source_type: str,
        status: str,
        active: bool,
        parent=None,
        *,
        chunk_count: int | None = None,
        collection: str | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("sourceListItem")
        self._path = path
        self._active = active
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._setup_ui(name, source_type, status, chunk_count, collection)

    def _setup_ui(
        self,
        name: str,
        source_type: str,
        status: str,
        chunk_count: int | None,
        collection: str | None,
    ):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        display_name = (name or "Quelle")[:60] + ("…" if len(name or "") > 60 else "")
        self._name = QLabel(display_name)
        self._name.setObjectName("sourceItemName")
        self._name.setStyleSheet("font-size: 13px; font-weight: 500; color: #1f2937;")
        self._name.setWordWrap(True)
        layout.addWidget(self._name)

        meta_parts = []
        type_key = (source_type or "").lower()
        meta_parts.append(TYPE_LABELS.get(type_key, source_type or "Quelle"))
        meta_parts.append(STATUS_LABELS.get(status, status or "—"))
        if chunk_count is not None:
            meta_parts.append(_format_chunk_count(chunk_count))
        if collection:
            meta_parts.append(collection)
        self._meta = QLabel(" · ".join(meta_parts))
        self._meta.setObjectName("sourceItemMeta")
        self._meta.setStyleSheet("font-size: 11px; color: #64748b;")
        layout.addWidget(self._meta)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def _apply_style(self) -> None:
        base = """
            #sourceListItem {
                background: transparent;
                border-radius: 8px;
                border: none;
            }
            #sourceListItem:hover {
                background: #f1f5f9;
            }
            #sourceListItem[active="true"] {
                background: #dbeafe;
                border-left: 3px solid #2563eb;
            }
            #sourceListItem[active="true"] #sourceItemName {
                color: #1e40af;
            }
        """
        self.setStyleSheet(base)
        self.setProperty("active", self._active)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply_style()

    def _show_context_menu(self, pos) -> None:
        """D37: Context menu for Delete, Reindex."""
        menu = QMenu(self)
        delete_action = menu.addAction("Löschen")
        reindex_action = menu.addAction("Neu indexieren")
        action = menu.exec(self.mapToGlobal(pos))
        if action == delete_action:
            self._on_delete_requested()
        elif action == reindex_action:
            self._on_reindex_requested()

    def _on_delete_requested(self) -> None:
        """Emits delete signal or delegates to parent. Placeholder for future wiring."""
        if hasattr(self.parent(), "on_source_delete_requested"):
            self.parent().on_source_delete_requested(self._path)
        # No-op if parent does not handle; future: connect to KnowledgeWorkspace

    def _on_reindex_requested(self) -> None:
        """Emits reindex signal or delegates to parent. Placeholder for future wiring."""
        if hasattr(self.parent(), "on_source_reindex_requested"):
            self.parent().on_source_reindex_requested(self._path)
        # No-op if parent does not handle; future: connect to KnowledgeWorkspace

    @property
    def path(self) -> str:
        return self._path

    @property
    def source_id(self) -> str:
        """Alias for path (API compatibility)."""
        return self._path
