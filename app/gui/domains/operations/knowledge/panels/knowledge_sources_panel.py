"""
KnowledgeSourcesPanel – Registrierte Quellen / Dokumente.

Liste der Quellen, Hinzufügen-Button.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QFileDialog,
)
from PySide6.QtCore import Signal, Qt


def _panel_style() -> str:
    return (
        "background: white; border: 1px solid #e5e7eb; border-radius: 10px; "
        "padding: 12px;"
    )


class KnowledgeSourcesPanel(QFrame):
    """Quellen / Dokumente eines Collections."""

    source_selected = Signal(str)
    add_source_requested = Signal(str)  # path (file or dir)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("knowledgeSourcesPanel")
        self.setMinimumHeight(180)
        self._current_space: str | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        row = QHBoxLayout()
        title = QLabel("Quellen")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        row.addWidget(title)
        row.addStretch()

        btn_file = QPushButton("+ Datei")
        btn_file.setObjectName("addFileButton")
        btn_file.setStyleSheet(
            """
            #addFileButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            #addFileButton:hover { background: #1d4ed8; }
            """
        )
        btn_file.clicked.connect(self._on_add_file)
        row.addWidget(btn_file)

        btn_dir = QPushButton("+ Ordner")
        btn_dir.setObjectName("addDirButton")
        btn_dir.setStyleSheet(
            """
            #addDirButton {
                background: #059669;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            #addDirButton:hover { background: #047857; }
            """
        )
        btn_dir.clicked.connect(self._on_add_dir)
        row.addWidget(btn_dir)
        layout.addLayout(row)

        self._list = QListWidget()
        self._list.setObjectName("sourcesList")
        self._list.setSpacing(2)
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.setStyleSheet(
            "QListWidget { background: #fafafa; border: none; border-radius: 6px; }"
        )
        layout.addWidget(self._list, 1)

    def _on_item_clicked(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.source_selected.emit(path)

    def _on_add_file(self) -> None:
        """Öffnet Dateiauswahl."""
        if not self._current_space:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Dokument hinzufügen",
            "",
            "Unterstützte Dateien (*.md *.txt *.py *.json);;Alle (*.*)",
        )
        if path:
            self.add_source_requested.emit(path)

    def _on_add_dir(self) -> None:
        """Öffnet Ordnerauswahl."""
        if not self._current_space:
            return
        path = QFileDialog.getExistingDirectory(self, "Ordner hinzufügen", "")
        if path:
            self.add_source_requested.emit(path)

    def set_space(self, space: str) -> None:
        """Setzt die aktuelle Collection."""
        self._current_space = space
        self._load_sources()

    def _load_sources(self) -> None:
        """Lädt Quellen für die aktuelle Collection."""
        self._list.clear()
        if not self._current_space:
            return
        try:
            from app.services.knowledge_service import get_knowledge_service
            backend = get_knowledge_service()
            sources = backend.list_sources(self._current_space)
            for s in sources:
                name = s.get("name", Path(s.get("path", "")).name)
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, s.get("path", ""))
                item.setToolTip(s.get("path", ""))
                self._list.addItem(item)
        except Exception:
            pass

    def refresh(self) -> None:
        """Aktualisiert die Quellenliste."""
        self._load_sources()
