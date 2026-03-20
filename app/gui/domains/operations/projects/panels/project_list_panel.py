"""
ProjectListPanel – Liste der Projekte mit Anlegen und Auswahl.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QFrame,
    QLineEdit,
)
from PySide6.QtCore import Signal, Qt
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


class ProjectListPanel(QFrame):
    """Panel für Projektliste. Links im Projects-Workspace."""

    project_selected = Signal(object)  # project dict or None
    new_project_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectListPanel")
        self.setMinimumWidth(240)
        self.setMaximumWidth(320)
        self._current_project_id = None
        self._setup_ui()
        self._load_projects()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("Projekte")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(header)

        btn_row = QHBoxLayout()
        btn_new = QPushButton("Neues Projekt")
        btn_new.setObjectName("newProjectButton")
        btn_new.setIcon(IconManager.get(IconRegistry.ADD, size=16))
        btn_new.setStyleSheet(
            """
            #newProjectButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 500;
            }
            #newProjectButton:hover { background: #1d4ed8; }
            """
        )
        btn_new.clicked.connect(self._on_new_project)
        btn_row.addWidget(btn_new)
        layout.addLayout(btn_row)

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Projekte filtern…")
        self._filter.textChanged.connect(self._on_filter_changed)
        self._filter.setStyleSheet(
            """
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus { border-color: #2563eb; }
            """
        )
        layout.addWidget(self._filter)

        self._list = QListWidget()
        self._list.setObjectName("projectList")
        self._list.setSpacing(2)
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.setStyleSheet(
            """
            #projectList {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 4px;
            }
            #projectList::item {
                padding: 10px 12px;
                border-radius: 6px;
            }
            #projectList::item:hover { background: #f3f4f6; }
            #projectList::item:selected { background: #dbeafe; }
            """
        )
        layout.addWidget(self._list, 1)

    def _load_projects(self) -> None:
        """Lädt Projekte aus der Datenbank."""
        self._list.clear()
        try:
            from app.services.project_service import get_project_service
            svc = get_project_service()
            filter_text = self._filter.text().strip()
            projects = svc.list_projects(filter_text)
            first_project = None
            for proj in projects:
                pid = proj.get("project_id")
                name = proj.get("name", "Projekt")
                if pid is not None:
                    if first_project is None:
                        first_project = proj
                    item = QListWidgetItem(name)
                    item.setData(Qt.ItemDataRole.UserRole, proj)
                    self._list.addItem(item)
            if first_project and self._current_project_id is None:
                self._current_project_id = first_project.get("project_id")
                self._list.blockSignals(True)
                self._list.setCurrentRow(0)
                self._list.blockSignals(False)
                self.project_selected.emit(first_project)
        except Exception:
            pass

    def _on_filter_changed(self, _text: str) -> None:
        self._load_projects()

    def _on_item_clicked(self, item: QListWidgetItem):
        proj = item.data(Qt.ItemDataRole.UserRole)
        if proj is not None:
            self._current_project_id = proj.get("project_id")
            self.project_selected.emit(proj)

    def _on_new_project(self) -> None:
        self.new_project_requested.emit()

    def refresh(self) -> None:
        """Aktualisiert die Projektliste."""
        self._load_projects()

    def set_current(self, project_id: int | None) -> None:
        """Setzt die visuelle Auswahl ohne Signal."""
        self._current_project_id = project_id
        for i in range(self._list.count()):
            item = self._list.item(i)
            proj = item.data(Qt.ItemDataRole.UserRole)
            if proj and proj.get("project_id") == project_id:
                self._list.blockSignals(True)
                self._list.setCurrentRow(i)
                self._list.blockSignals(False)
                return
        self._list.clearSelection()
