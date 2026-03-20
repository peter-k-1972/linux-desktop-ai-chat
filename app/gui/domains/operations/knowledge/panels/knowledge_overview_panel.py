"""
KnowledgeOverviewPanel – Zusammenfassung.

Spaces, Chunks, Quellen, Status.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt


def _panel_style() -> str:
    return (
        "background: white; border: 1px solid #e5e7eb; border-radius: 10px; "
        "padding: 12px;"
    )


class KnowledgeOverviewPanel(QFrame):
    """Übersicht: Spaces, Chunks, Quellen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("knowledgeOverviewPanel")
        self.setMinimumHeight(120)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Übersicht")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        self._row = QHBoxLayout()
        self._spaces_label = QLabel("—")
        self._chunks_label = QLabel("—")
        self._sources_label = QLabel("—")
        for lbl in [self._spaces_label, self._chunks_label, self._sources_label]:
            lbl.setStyleSheet("color: #6b7280; font-size: 12px;")
        self._row.addWidget(self._spaces_label)
        self._row.addWidget(self._chunks_label)
        self._row.addWidget(self._sources_label)
        self._row.addStretch()
        layout.addLayout(self._row)

    def refresh(self, project_id: int | None = None) -> None:
        """Lädt Übersicht aus dem Backend. project_id: bei aktivem Projekt."""
        try:
            from app.services.knowledge_service import get_knowledge_service
            backend = get_knowledge_service()
            overview = backend.get_overview(project_id)
            self._spaces_label.setText(f"Spaces: {len(overview['spaces'])}")
            self._chunks_label.setText(f"Chunks: {overview['total_chunks']}")
            self._sources_label.setText(f"Quellen: {overview['total_sources']}")
        except Exception:
            self._spaces_label.setText("Spaces: —")
            self._chunks_label.setText("Chunks: —")
            self._sources_label.setText("Quellen: —")
