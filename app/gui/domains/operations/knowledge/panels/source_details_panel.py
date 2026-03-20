"""
SourceDetailsPanel – Right-side panel showing source metadata and actions.

Displays: name, type, size, collection, created date, chunk count, embedding model.
Actions: Re-index, Delete, Open.
Updates when the selected source changes.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.widgets import EmptyStateWidget


def _format_size(size_bytes: int) -> str:
    """Format file size for display."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def _format_date(ts: Optional[float]) -> str:
    """Format timestamp for display."""
    if ts is None:
        return "—"
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError):
        return "—"


def _get_embedding_model() -> str:
    """Get the default embedding model name."""
    try:
        from app.rag.embedding_service import DEFAULT_EMBEDDING_MODEL
        return DEFAULT_EMBEDDING_MODEL
    except Exception:
        return "nomic-embed-text"


def _get_source_size(path: str, source_type: str) -> Optional[int]:
    """Get size for file/folder. Returns None for url/note."""
    if source_type in ("url", "note", "quelle"):
        return None
    try:
        p = Path(path)
        if not p.exists():
            return None
        if p.is_file():
            return p.stat().st_size
        # Folder: approximate as sum of file sizes (limit traversal)
        total = 0
        for i, f in enumerate(p.rglob("*")):
            if i > 5000:  # limit files
                return total
            if f.is_file():
                total += f.stat().st_size
                if total > 100 * 1024 * 1024:  # cap at 100MB
                    return total
        return total
    except Exception:
        return None


def _get_source_created(path: str, source_type: str) -> Optional[float]:
    """Get created/mtime for file/folder. Returns None for url/note."""
    if source_type in ("url", "note", "quelle"):
        return None
    try:
        p = Path(path)
        if not p.exists():
            return None
        return p.stat().st_mtime
    except Exception:
        return None


TYPE_LABELS = {
    "datei": "File",
    "ordner": "Folder",
    "file": "File",
    "folder": "Folder",
    "url": "URL",
    "note": "Note",
    "quelle": "Source",
}


class SourceDetailsPanel(QFrame):
    """
    Right-side details panel for the selected source.

    Shows metadata and action buttons. Updates when set_source() is called.
    """

    reindex_requested = Signal(str)  # source_id
    delete_requested = Signal(str)  # source_id
    open_requested = Signal(str)    # source_id
    view_chunks_requested = Signal()  # Show chunk viewer for current source

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sourceDetailsPanel")
        self.setMinimumWidth(200)
        self.setMaximumWidth(320)
        self._current_source: Optional[Dict[str, Any]] = None
        self._project_id: Optional[int] = None
        self._collection: Optional[str] = None
        self._chunk_count: Optional[int] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Source Details")
        title.setObjectName("sourceDetailsTitle")
        title.setStyleSheet("""
            #sourceDetailsTitle {
                font-size: 14px;
                font-weight: 600;
                color: #334155;
            }
        """)
        layout.addWidget(title)

        self._placeholder = EmptyStateWidget(
            title="Quelldetails",
            description="Wähle eine Quelle in der Liste, um Details anzuzeigen.",
            compact=True,
            parent=self,
        )
        layout.addWidget(self._placeholder)

        self._content = QWidget()
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        self._name_label = QLabel()
        self._name_label.setWordWrap(True)
        self._name_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1f2937;")
        content_layout.addWidget(self._name_label)

        self._meta_labels: Dict[str, QLabel] = {}
        for key in ("type", "size", "collection", "created", "chunk_count", "embedding_model"):
            row = QHBoxLayout()
            key_label = QLabel(f"{key.replace('_', ' ').title()}:")
            key_label.setStyleSheet("font-size: 11px; color: #64748b; min-width: 90px;")
            val_label = QLabel("—")
            val_label.setWordWrap(True)
            val_label.setStyleSheet("font-size: 11px; color: #334155;")
            row.addWidget(key_label)
            row.addWidget(val_label, 1)
            content_layout.addLayout(row)
            self._meta_labels[key] = val_label

        content_layout.addSpacing(12)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        self._btn_reindex = QPushButton("Re-index Source")
        self._btn_reindex.setIcon(IconManager.get(IconRegistry.REFRESH, size=14))
        self._btn_reindex.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                font-size: 12px;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QPushButton:hover { background: #f1f5f9; }
        """)
        self._btn_reindex.clicked.connect(self._on_reindex)
        btn_layout.addWidget(self._btn_reindex)

        self._btn_open = QPushButton("Open Source")
        self._btn_open.setIcon(IconManager.get(IconRegistry.SEARCH, size=14))
        self._btn_open.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                font-size: 12px;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QPushButton:hover { background: #f1f5f9; }
        """)
        self._btn_open.clicked.connect(self._on_open)
        btn_layout.addWidget(self._btn_open)

        self._btn_delete = QPushButton("Delete Source")
        self._btn_delete.setIcon(IconManager.get(IconRegistry.REMOVE, size=14))
        self._btn_delete.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                font-size: 12px;
                background: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 6px;
                color: #b91c1c;
            }
            QPushButton:hover { background: #fee2e2; }
        """)
        self._btn_delete.clicked.connect(self._on_delete)
        btn_layout.addWidget(self._btn_delete)

        self._btn_chunks = QPushButton("View Chunks")
        self._btn_chunks.setIcon(IconManager.get(IconRegistry.SEARCH, size=14))
        self._btn_chunks.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                font-size: 12px;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QPushButton:hover { background: #f1f5f9; }
        """)
        self._btn_chunks.clicked.connect(self.view_chunks_requested.emit)
        btn_layout.addWidget(self._btn_chunks)

        content_layout.addLayout(btn_layout)
        content_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(self._content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll, 1)
        self._content_scroll = scroll

        self._content.hide()

        self.setStyleSheet("""
            #sourceDetailsPanel {
                background: #f8fafc;
                border-left: 1px solid #e2e8f0;
            }
        """)

    def set_source(
        self,
        source: Optional[Dict[str, Any]],
        project_id: Optional[int] = None,
        collection: Optional[str] = None,
        chunk_count: Optional[int] = None,
    ) -> None:
        """
        Update the panel with the selected source.
        Call with None to show the placeholder.
        """
        self._current_source = source
        self._project_id = project_id
        self._collection = collection
        self._chunk_count = chunk_count

        if source is None:
            self._placeholder.show()
            self._content.hide()
            return

        self._placeholder.hide()
        self._content.show()

        path = source.get("path", "")
        name = source.get("name", Path(path).name if path else "Source")
        source_type = source.get("type", "quelle")

        self._name_label.setText(name[:80] + ("…" if len(name) > 80 else ""))

        self._meta_labels["type"].setText(TYPE_LABELS.get(source_type, source_type))

        size = _get_source_size(path, source_type)
        self._meta_labels["size"].setText(_format_size(size) if size is not None else "—")

        self._meta_labels["collection"].setText(collection or "—")

        created = _get_source_created(path, source_type)
        self._meta_labels["created"].setText(_format_date(created))

        self._meta_labels["chunk_count"].setText(
            str(chunk_count) if chunk_count is not None else "—"
        )

        self._meta_labels["embedding_model"].setText(_get_embedding_model())

        # Open only for files/folders
        can_open = source_type in ("datei", "ordner", "file", "folder") and path
        self._btn_open.setEnabled(bool(can_open))

        # View Chunks only for files/folders
        can_view_chunks = source_type in ("datei", "ordner", "file", "folder") and path
        self._btn_chunks.setEnabled(bool(can_view_chunks))

    def _on_reindex(self) -> None:
        if self._current_source:
            path = self._current_source.get("path", "")
            if path:
                self.reindex_requested.emit(path)

    def _on_delete(self) -> None:
        if self._current_source:
            path = self._current_source.get("path", "")
            if path:
                self.delete_requested.emit(path)

    def _on_open(self) -> None:
        if self._current_source:
            path = self._current_source.get("path", "")
            source_type = self._current_source.get("type", "")
            if not path:
                return
            if source_type in ("url",):
                url = QUrl(path)
                if url.isValid():
                    QDesktopServices.openUrl(url)
            else:
                p = Path(path)
                if p.exists():
                    url = QUrl.fromLocalFile(str(p.resolve()))
                    QDesktopServices.openUrl(url)
