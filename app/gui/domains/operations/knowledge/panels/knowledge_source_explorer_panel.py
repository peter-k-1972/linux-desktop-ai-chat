"""
KnowledgeSourceExplorerPanel – Projektbezogener Wissensquellen-Explorer.

Zeigt nur Quellen des aktiven Projekts. Projektkontext sichtbar.
Collection = project_{id}, Status pro Quelle.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QFileDialog,
    QScrollArea,
)
from PySide6.QtCore import Signal, Qt

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.shared import apply_header_layout, apply_sidebar_layout
from app.gui.widgets import EmptyStateWidget
from app.gui.domains.operations.knowledge.panels.source_list_item import SourceListItemWidget


class KnowledgeSourceExplorerPanel(QFrame):
    """Projektbezogener Quellen-Explorer. Links im Knowledge-Workspace."""

    source_selected = Signal(str)
    add_source_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("knowledgeSourceExplorerPanel")
        self.setMinimumWidth(240)
        self.setMaximumWidth(320)
        self._project_id: int | None = None
        self._project_name: str | None = None
        self._current_source: str | None = None
        self._source_widgets: dict[str, SourceListItemWidget] = {}
        self._setup_ui()
        self._connect_project_context()
        self._load_sources()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        apply_sidebar_layout(layout)

        self._project_header = QFrame()
        self._project_header.setObjectName("knowledgeExplorerProjectHeader")
        header_layout = QVBoxLayout(self._project_header)
        apply_header_layout(header_layout)
        self._project_label = QLabel("Bitte Projekt auswählen")
        self._project_label.setObjectName("knowledgeExplorerProjectLabel")
        self._project_label.setStyleSheet("""
            #knowledgeExplorerProjectLabel {
                font-size: 13px;
                font-weight: 600;
                color: #64748b;
            }
        """)
        self._project_label.setWordWrap(True)
        header_layout.addWidget(self._project_label)
        self._project_header.setStyleSheet("""
            #knowledgeExplorerProjectHeader {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self._project_header)

        self._collection_info = QLabel("")
        self._collection_info.setStyleSheet("font-size: 11px; color: #64748b;")
        self._collection_info.hide()
        layout.addWidget(self._collection_info)

        btn_row = QHBoxLayout()
        self._btn_file = QPushButton("+ Datei")
        self._btn_file.setIcon(IconManager.get(IconRegistry.ADD, size=14))
        self._btn_file.setEnabled(False)
        self._btn_file.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self._btn_file.clicked.connect(self._on_add_file)
        btn_row.addWidget(self._btn_file)

        self._btn_dir = QPushButton("+ Ordner")
        self._btn_dir.setIcon(IconManager.get(IconRegistry.ADD, size=14))
        self._btn_dir.setEnabled(False)
        self._btn_dir.setStyleSheet("""
            QPushButton {
                background: #059669;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background: #047857; }
            QPushButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self._btn_dir.clicked.connect(self._on_add_dir)
        btn_row.addWidget(self._btn_dir)
        layout.addLayout(btn_row)

        sources_title = QLabel("Quellen")
        sources_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #64748b;")
        layout.addWidget(sources_title)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._list_content = QWidget()
        self._list_layout = QVBoxLayout(self._list_content)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._scroll.setWidget(self._list_content)
        layout.addWidget(self._scroll, 1)

        self._empty_widget = EmptyStateWidget(
            title="",
            description="",
            compact=True,
            parent=self,
        )
        self._empty_widget.hide()

        self.setStyleSheet("""
            #knowledgeSourceExplorerPanel {
                background: #ffffff;
                border-right: 1px solid #e2e8f0;
            }
        """)

    def _connect_project_context(self) -> None:
        try:
            from app.gui.events.project_events import subscribe_project_events
            from app.core.context.project_context_manager import get_project_context_manager
            subscribe_project_events(self._on_project_context_changed)
            mgr = get_project_context_manager()
            pid = mgr.get_active_project_id()
            proj = mgr.get_active_project()
            self._on_project_changed(pid, proj)
        except Exception:
            pass

    def _on_project_context_changed(self, payload: dict) -> None:
        project_id = payload.get("project_id")
        if project_id is None:
            self._on_project_changed(None, None)
            return
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            project = get_project_context_manager().get_active_project()
            self._on_project_changed(project_id, project)
        except Exception:
            self._on_project_changed(None, None)

    def _on_project_changed(self, project_id, project) -> None:
        if project and isinstance(project, dict):
            self._project_id = project.get("project_id")
            self._project_name = project.get("name", "Projekt")
            self._project_label.setText(self._project_name)
            self._project_label.setStyleSheet("""
                #knowledgeExplorerProjectLabel {
                    font-size: 13px;
                    font-weight: 600;
                    color: #1f2937;
                }
            """)
            self._btn_file.setEnabled(True)
            self._btn_dir.setEnabled(True)
        else:
            self._project_id = None
            self._project_name = None
            self._project_label.setText("Bitte Projekt auswählen")
            self._project_label.setStyleSheet("""
                #knowledgeExplorerProjectLabel {
                    font-size: 13px;
                    font-weight: 600;
                    color: #64748b;
                }
            """)
            self._btn_file.setEnabled(False)
            self._btn_dir.setEnabled(False)
            self._collection_info.hide()
        self._load_sources()

    def _load_sources(self) -> None:
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._source_widgets.clear()

        if self._project_id is None:
            self._empty_widget.set_content(
                "Kein Projekt ausgewählt",
                "Wähle ein Projekt, um Quellen anzuzeigen.",
            )
            self._empty_widget.setParent(None)
            self._list_layout.addWidget(self._empty_widget)
            self._empty_widget.show()
            return

        try:
            from app.services.knowledge_service import get_knowledge_service
            svc = get_knowledge_service()
            sources = svc.list_sources_for_project(self._project_id)
            collections = svc.list_collections(self._project_id)
            coll_by_id = {c.get("id"): c.get("name", "?") for c in collections}
            chunk_count = svc.get_project_chunk_count(self._project_id)
            space = svc.get_space_for_project(self._project_id)
            self._collection_info.setText(f"Collection: {space} · {chunk_count} Chunks")
            self._collection_info.show()
        except Exception:
            sources = []
            coll_by_id = {}
            self._collection_info.hide()

        if not sources:
            self._empty_widget.set_content(
                "Keine Quellen",
                "Datei oder Ordner hinzufügen.",
            )
            self._empty_widget.setParent(None)
            self._list_layout.addWidget(self._empty_widget)
            self._empty_widget.show()
            return

        self._empty_widget.hide()
        for s in sources:
            path = s.get("path", "")
            name = s.get("name", Path(path).name if path else "Quelle")
            source_type = s.get("type", "quelle")
            status = s.get("status", "indexiert")
            cid = s.get("collection_id")
            collection = coll_by_id.get(cid, "—") if cid else None
            active = path == self._current_source
            item = SourceListItemWidget(
                path, name, source_type, status, active, self,
                chunk_count=s.get("chunk_count"),  # per-source if available
                collection=collection,
            )
            item.mousePressEvent = lambda e, p=path: self._on_item_clicked(p)
            self._source_widgets[path] = item
            self._list_layout.addWidget(item)

        self._list_layout.addStretch()

    def _on_item_clicked(self, path: str) -> None:
        for wid in self._source_widgets.values():
            wid.set_active(wid.path == path)
        self._current_source = path
        self.source_selected.emit(path)

    def _on_add_file(self) -> None:
        if self._project_id is None:
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
        if self._project_id is None:
            return
        path = QFileDialog.getExistingDirectory(self, "Ordner hinzufügen", "")
        if path:
            self.add_source_requested.emit(path)

    def refresh(self) -> None:
        self._load_sources()

    def select_source(self, path: str) -> None:
        """Wählt eine Quelle per Pfad (z.B. aus Project Hub)."""
        self._load_sources()
        if path in self._source_widgets:
            self._on_item_clicked(path)

    def get_current_space(self) -> str | None:
        """Space für das aktive Projekt (project_{id})."""
        if self._project_id is None:
            return None
        try:
            from app.services.knowledge_service import get_knowledge_service
            return get_knowledge_service().get_space_for_project(self._project_id)
        except Exception:
            return None
