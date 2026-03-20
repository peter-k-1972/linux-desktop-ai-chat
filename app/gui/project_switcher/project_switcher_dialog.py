"""
ProjectSwitcherDialog – Dialog zum Wechseln des aktiven Projekts.

Enthält: Suchfeld, Recent Projects, All Projects, Create New Project.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QFrame,
    QScrollArea,
    QWidget,
    QFormLayout,
    QDialogButtonBox,
    QTextEdit,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


class NewProjectDialog(QDialog):
    """Dialog zum Anlegen eines neuen Projekts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neues Projekt")
        self.setMinimumWidth(360)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QFormLayout(self)
        self._name = QLineEdit()
        self._name.setPlaceholderText("z.B. Marketing-Kampagne Q2")
        layout.addRow("Name:", self._name)

        self._desc = QTextEdit()
        self._desc.setPlaceholderText("Optionale Beschreibung…")
        self._desc.setMaximumHeight(80)
        layout.addRow("Beschreibung:", self._desc)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_name(self) -> str:
        return (self._name.text() or "").strip()

    def get_description(self) -> str:
        return (self._desc.toPlainText() or "").strip()


class ProjectSwitcherDialog(QDialog):
    """
    Dialog zum Wechseln des aktiven Projekts.

    - Suchfeld
    - Recent projects
    - All projects
    - Create new project button
    """

    project_selected = Signal(object)  # project_id or None for clear

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Projekt wechseln")
        self.setMinimumSize(380, 420)
        self.setModal(True)
        self._recent_limit = 5
        self._setup_ui()
        self._load_projects()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Search field
        self._search = QLineEdit()
        self._search.setPlaceholderText("Projekte durchsuchen…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_search_changed)
        search_icon = IconManager.get(IconRegistry.SEARCH, size=18)
        if search_icon:
            self._search.addAction(search_icon, QLineEdit.ActionPosition.LeadingPosition)
        layout.addWidget(self._search)

        # Recent projects section
        recent_label = QLabel("Zuletzt verwendet")
        recent_label.setObjectName("projectSectionLabel")
        layout.addWidget(recent_label)
        self._recent_list = QListWidget()
        self._recent_list.setObjectName("projectList")
        self._recent_list.itemClicked.connect(self._on_project_clicked)
        layout.addWidget(self._recent_list)

        # All projects section
        all_label = QLabel("Alle Projekte")
        all_label.setObjectName("projectSectionLabel")
        layout.addWidget(all_label)
        self._all_list = QListWidget()
        self._all_list.setObjectName("projectList")
        self._all_list.itemClicked.connect(self._on_project_clicked)
        layout.addWidget(self._all_list, 1)

        # Create new project button
        self._btn_new = QPushButton("+ Neues Projekt anlegen")
        self._btn_new.setIcon(IconManager.get(IconRegistry.ADD, size=16))
        self._btn_new.clicked.connect(self._on_create_new)
        layout.addWidget(self._btn_new)

        # Clear project button
        self._btn_clear = QPushButton("Projektkontext aufheben")
        self._btn_clear.clicked.connect(self._on_clear)
        layout.addWidget(self._btn_clear)

        self.setStyleSheet("""
            #projectSectionLabel {
                font-weight: 600;
                font-size: 11px;
                color: #64748b;
                margin-top: 4px;
            }
            #projectList {
                background: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
            }
            #projectList::item {
                padding: 8px 12px;
                border-radius: 6px;
            }
            #projectList::item:hover {
                background: #f1f5f9;
            }
            #projectList::item:selected {
                background: #3b82f6;
                color: white;
            }
        """)

    def _load_projects(self) -> None:
        """Lädt Projekte aus dem ProjectService."""
        try:
            from app.services.project_service import get_project_service
            svc = get_project_service()
            all_projects = svc.list_projects()
        except Exception:
            all_projects = []

        # Recent: first N by updated_at (or created_at)
        recent = sorted(
            all_projects,
            key=lambda p: p.get("updated_at") or p.get("created_at") or "",
            reverse=True,
        )[: self._recent_limit]

        self._all_projects = all_projects
        self._recent_projects = recent
        self._apply_filter(self._search.text())

    def _apply_filter(self, filter_text: str) -> None:
        """Aktualisiert die Listen basierend auf Suchfilter."""
        q = (filter_text or "").strip().lower()

        def matches(proj: Dict[str, Any]) -> bool:
            if not q:
                return True
            name = (proj.get("name") or "").lower()
            desc = (proj.get("description") or "").lower()
            return q in name or q in desc

        recent_filtered = [p for p in self._recent_projects if matches(p)]
        all_filtered = [p for p in self._all_projects if matches(p)]

        self._populate_list(self._recent_list, recent_filtered)
        self._populate_list(self._all_list, all_filtered)

    def _populate_list(
        self, list_widget: QListWidget, projects: List[Dict[str, Any]]
    ) -> None:
        list_widget.clear()
        for proj in projects:
            name = proj.get("name", "Projekt")
            pid = proj.get("project_id")
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, proj)
            list_widget.addItem(item)

    def _on_search_changed(self, text: str) -> None:
        self._apply_filter(text)

    def _on_project_clicked(self, item: QListWidgetItem) -> None:
        proj = item.data(Qt.ItemDataRole.UserRole)
        if proj and isinstance(proj, dict):
            pid = proj.get("project_id")
            if pid is not None:
                self.project_selected.emit(pid)
                self.accept()

    def _on_create_new(self) -> None:
        dlg = NewProjectDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name = dlg.get_name()
        if not name:
            return
        try:
            from app.services.project_service import get_project_service
            svc = get_project_service()
            desc = dlg.get_description()
            project_id = svc.create_project(name, desc)
            self.project_selected.emit(project_id)
            self.accept()
        except Exception:
            pass

    def _on_clear(self) -> None:
        """Hebt den Projektkontext auf."""
        self.project_selected.emit(None)
        self.accept()
