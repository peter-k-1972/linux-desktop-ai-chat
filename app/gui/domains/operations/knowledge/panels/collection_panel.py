"""
CollectionPanel – Collections page for Knowledge workspace.

Flat list of collections. Create, rename, delete, assign sources.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QFrame,
    QLabel,
    QMenu,
    QDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry

from app.gui.domains.operations.knowledge.panels.collection_dialog import (
    CreateCollectionDialog,
    RenameCollectionDialog,
    AssignSourcesDialog,
)


class CollectionItemWidget(QFrame):
    """Single collection row with name and source count."""

    def __init__(
        self,
        collection: Dict[str, Any],
        source_count: int,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("collectionItem")
        self._collection = collection
        self._source_count = source_count
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        self._name = QLabel(self._collection.get("name", "Unnamed"))
        self._name.setStyleSheet("font-size: 13px; font-weight: 500; color: #1f2937;")
        self._name.setWordWrap(True)
        layout.addWidget(self._name, 1)

        count = QLabel(f"{self._source_count} sources")
        count.setStyleSheet("font-size: 11px; color: #64748b;")
        layout.addWidget(count)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            #collectionItem {
                background: transparent;
                border-radius: 8px;
                border: none;
            }
            #collectionItem:hover {
                background: #f1f5f9;
            }
        """)

    @property
    def collection(self) -> Dict[str, Any]:
        return self._collection


class CollectionPanel(QFrame):
    """
    Collections panel: flat list, create, rename, delete, assign sources.
    """

    collection_selected = Signal(str)  # collection_id
    collections_changed = Signal()  # Emitted when create/rename/delete/assign

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("collectionPanel")
        self._project_id: Optional[int] = None
        self._item_widgets: Dict[str, CollectionItemWidget] = {}
        self._setup_ui()
        self._connect_project_context()

    def _connect_project_context(self) -> None:
        try:
            from app.gui.events.project_events import subscribe_project_events
            subscribe_project_events(self._on_project_context_changed)
            from app.core.context.project_context_manager import get_project_context_manager
            self._project_id = get_project_context_manager().get_active_project_id()
            self._load_collections()
        except Exception:
            pass

    def _on_project_context_changed(self, payload: dict) -> None:
        self._project_id = payload.get("project_id")
        self._load_collections()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Collections")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #0f172a;")
        header.addWidget(title)
        header.addStretch()

        self._btn_create = QPushButton("+ Create Collection")
        self._btn_create.setIcon(IconManager.get(IconRegistry.ADD, size=16))
        self._btn_create.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self._btn_create.clicked.connect(self._on_create)
        self._btn_create.setEnabled(self._project_id is not None)
        header.addWidget(self._btn_create)
        layout.addLayout(header)

        self._empty_label = QLabel("No project selected. Select a project to manage collections.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #94a3b8; font-size: 13px; padding: 24px;")
        layout.addWidget(self._empty_label)

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
        self._scroll.hide()

        self.setStyleSheet("""
            #collectionPanel {
                background: #ffffff;
            }
        """)

    def _load_collections(self) -> None:
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._item_widgets.clear()

        self._btn_create.setEnabled(self._project_id is not None)

        if self._project_id is None:
            self._empty_label.setText("No project selected. Select a project to manage collections.")
            self._empty_label.show()
            self._scroll.hide()
            return

        try:
            from app.services.knowledge_service import get_knowledge_service
            svc = get_knowledge_service()
            collections = svc.list_collections(self._project_id)
            sources = svc.list_sources_for_project(self._project_id)
            source_counts = {}
            for s in sources:
                cid = s.get("collection_id")
                if cid:
                    source_counts[cid] = source_counts.get(cid, 0) + 1
        except Exception:
            collections = []
            source_counts = {}

        if not collections:
            self._empty_label.setText("No collections yet. Click + Create Collection to add one.")
            self._empty_label.show()
            self._scroll.hide()
            return

        self._empty_label.hide()
        self._scroll.show()

        for coll in collections:
            cid = coll.get("id", "")
            count = source_counts.get(cid, 0)
            item = CollectionItemWidget(coll, count, self)
            item.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            item.customContextMenuRequested.connect(
                lambda pos, it=item, c=coll: self._show_context_menu(it, pos, c)
            )
            item.mousePressEvent = lambda e, cid=cid: self._on_item_clicked(e, cid)
            self._item_widgets[cid] = item
            self._list_layout.addWidget(item)

        self._list_layout.addStretch()

    def _on_item_clicked(self, event, collection_id: str) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.collection_selected.emit(collection_id)

    def _show_context_menu(
        self, widget: QWidget, pos, collection: Dict[str, Any]
    ) -> None:
        menu = QMenu(self)
        rename_act = QAction("Rename", self)
        rename_act.triggered.connect(lambda: self._on_rename(collection))
        menu.addAction(rename_act)

        assign_act = QAction("Assign Sources", self)
        assign_act.triggered.connect(lambda: self._on_assign_sources(collection))
        menu.addAction(assign_act)

        menu.addSeparator()

        delete_act = QAction("Delete", self)
        delete_act.triggered.connect(lambda: self._on_delete(collection))
        menu.addAction(delete_act)

        menu.exec(widget.mapToGlobal(pos))

    def _on_create(self) -> None:
        if self._project_id is None:
            return
        dlg = CreateCollectionDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = dlg.get_name()
            if name:
                try:
                    from app.services.knowledge_service import get_knowledge_service
                    get_knowledge_service().create_collection(self._project_id, name)
                    self._load_collections()
                    self.collections_changed.emit()
                except Exception:
                    pass

    def _on_rename(self, collection: Dict[str, Any]) -> None:
        if self._project_id is None:
            return
        cid = collection.get("id", "")
        current_name = collection.get("name", "")
        dlg = RenameCollectionDialog(current_name, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_name = dlg.get_name()
            if new_name:
                try:
                    from app.services.knowledge_service import get_knowledge_service
                    get_knowledge_service().rename_collection(
                        self._project_id, cid, new_name
                    )
                    self._load_collections()
                    self.collections_changed.emit()
                except Exception:
                    pass

    def _on_delete(self, collection: Dict[str, Any]) -> None:
        if self._project_id is None:
            return
        cid = collection.get("id", "")
        name = collection.get("name", "?")
        reply = QMessageBox.question(
            self,
            "Delete Collection",
            f"Delete collection \"{name}\"? Sources will be unassigned.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from app.services.knowledge_service import get_knowledge_service
                get_knowledge_service().delete_collection(self._project_id, cid)
                self._load_collections()
                self.collections_changed.emit()
            except Exception:
                pass

    def _on_assign_sources(self, collection: Dict[str, Any]) -> None:
        if self._project_id is None:
            return
        cid = collection.get("id", "")
        try:
            from app.services.knowledge_service import get_knowledge_service
            svc = get_knowledge_service()
            sources = svc.list_sources_for_project(self._project_id)
            assigned = [s.get("path") for s in sources if s.get("collection_id") == cid]
            dlg = AssignSourcesDialog(sources, collection, assigned, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                selected = dlg.get_selected_paths()
                # Unassign sources no longer selected
                for s in sources:
                    if s.get("collection_id") == cid and s.get("path") not in selected:
                        svc.assign_source_to_collection(self._project_id, s.get("path"), None)
                # Assign selected sources
                svc.assign_sources_to_collection(self._project_id, selected, cid)
                self._load_collections()
                self.collections_changed.emit()
        except Exception:
            pass

    def refresh(self) -> None:
        """Reload collections from service."""
        self._load_collections()
