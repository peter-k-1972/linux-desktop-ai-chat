"""
ChunkViewerPanel – Debug tool for viewing chunks of a selected source.

Displays chunk number and text snippet per chunk.
Useful for debugging chunk size and overlap behavior.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal

SNIPPET_LENGTH = 200  # Chars to show in list; full text in expanded view


class ChunkItemWidget(QFrame):
    """Single chunk row: number + text snippet."""

    def __init__(self, number: int, text: str, filename: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("chunkItem")
        self._full_text = text
        self._setup_ui(number, text, filename)

    def _setup_ui(self, number: int, text: str, filename: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        header = QHBoxLayout()
        num_label = QLabel(f"Chunk {number}")
        num_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #334155;")
        header.addWidget(num_label)
        if filename:
            file_label = QLabel(f"· {filename}")
            file_label.setStyleSheet("font-size: 11px; color: #64748b;")
            header.addWidget(file_label)
        header.addStretch()
        layout.addLayout(header)

        snippet = text[:SNIPPET_LENGTH] + ("…" if len(text) > SNIPPET_LENGTH else "")
        self._text_label = QLabel(snippet)
        self._text_label.setWordWrap(True)
        self._text_label.setStyleSheet("font-size: 12px; color: #475569; line-height: 1.4;")
        self._text_label.setToolTip(text)
        layout.addWidget(self._text_label)

        self.setStyleSheet("""
            #chunkItem {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            #chunkItem:hover {
                border-color: #cbd5e1;
                background: #f8fafc;
            }
        """)


class ChunkViewerPanel(QFrame):
    """
    Panel displaying chunks for a selected source.
    Re-chunks on the fly for debugging chunk size and overlap.
    """

    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chunkViewerPanel")
        self._project_id: Optional[int] = None
        self._current_source: Optional[Dict[str, Any]] = None
        self._setup_ui()

    def _on_back(self) -> None:
        self.back_requested.emit()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        self._title = QLabel("Chunk Viewer")
        self._title.setStyleSheet("font-size: 14px; font-weight: 600; color: #334155;")
        header.addWidget(self._title)
        header.addStretch()

        self._btn_back = QPushButton("← Back")
        self._btn_back.setStyleSheet("font-size: 12px; color: #64748b;")
        self._btn_back.clicked.connect(self._on_back)
        header.addWidget(self._btn_back)
        layout.addLayout(header)

        self._hint = QLabel("Select a source to view its chunks.")
        self._hint.setStyleSheet("font-size: 12px; color: #64748b;")
        layout.addWidget(self._hint)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._list_content = QWidget()
        self._list_layout = QVBoxLayout(self._list_content)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._scroll.setWidget(self._list_content)
        layout.addWidget(self._scroll, 1)
        self._scroll.hide()

        self.setStyleSheet("""
            #chunkViewerPanel {
                background: #f8fafc;
                border-left: 1px solid #e2e8f0;
            }
        """)

    def set_source(
        self,
        source: Optional[Dict[str, Any]],
        project_id: Optional[int] = None,
    ) -> None:
        """
        Load and display chunks for the given source.
        Call with None to show the placeholder.
        """
        self._current_source = source
        self._project_id = project_id

        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if source is None or project_id is None:
            self._hint.setText("Select a source to view its chunks.")
            self._hint.show()
            self._scroll.hide()
            return

        path = source.get("path", "")
        source_type = source.get("type", "quelle")
        name = source.get("name", Path(path).name if path else "Source")

        if source_type in ("url", "note", "quelle"):
            self._hint.setText(f"Chunk viewer supports files and folders only. \"{name}\" is a {source_type}.")
            self._hint.show()
            self._scroll.hide()
            return

        try:
            from app.services.knowledge_service import get_knowledge_service
            svc = get_knowledge_service()
            chunks = svc.get_chunks_for_source(project_id, path, source_type)
        except Exception as e:
            self._hint.setText(f"Error loading chunks: {e!s}")
            self._hint.show()
            self._scroll.hide()
            return

        if not chunks:
            self._hint.setText(f"No chunks for \"{name}\". File may be empty or unsupported.")
            self._hint.show()
            self._scroll.hide()
            return

        self._hint.setText(f"{len(chunks)} chunks for \"{name}\"")
        self._hint.show()
        self._scroll.show()

        for c in chunks:
            item = ChunkItemWidget(
                number=c.get("number", 0),
                text=c.get("text", ""),
                filename=c.get("filename", ""),
                parent=self,
            )
            self._list_layout.addWidget(item)

        self._list_layout.addStretch()
