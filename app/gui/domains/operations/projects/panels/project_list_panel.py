"""
ProjectListPanel – Projektarchiv-Liste (Projekte, Status, letzter Zugriff).
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Signal, Qt

from app.gui.domains.operations.projects.projects_list_sink import ProjectsListSink
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.shared.layout_constants import SIDEBAR_PADDING, WIDGET_SPACING
from app.gui.theme import design_metrics as dm
from app.ui_application.adapters.service_projects_overview_read_adapter import (
    ServiceProjectsOverviewReadAdapter,
)
from app.ui_application.presenters.projects_list_presenter import ProjectsListPresenter
from app.ui_application.ports.projects_overview_read_port import ProjectsOverviewReadPort
from app.ui_contracts.workspaces.projects_overview import ProjectListItem


class ProjectListPanel(QFrame):
    """Panel für Projektliste. Links im Projects-Workspace."""

    project_selected = Signal(object)  # project id or None
    new_project_requested = Signal()

    def __init__(
        self,
        parent=None,
        *,
        read_port: ProjectsOverviewReadPort | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("projectListPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(380)
        self._current_project_id = None
        self._items_by_project_id: dict[int, ProjectListItem] = {}
        self._setup_ui()
        self._sink = ProjectsListSink(self)
        self._presenter = ProjectsListPresenter(
            sink=self._sink,
            port=read_port or ServiceProjectsOverviewReadAdapter(),
        )
        self._presenter.attach()
        self.destroyed.connect(lambda: self._presenter.detach())

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            SIDEBAR_PADDING, SIDEBAR_PADDING, SIDEBAR_PADDING, SIDEBAR_PADDING
        )
        layout.setSpacing(WIDGET_SPACING)

        header = QLabel("Projektliste")
        header.setStyleSheet(
            f"font-weight: bold; font-size: {dm.TEXT_MD_PX}px; color: #1f2937;"
        )
        layout.addWidget(header)

        btn_row = QHBoxLayout()
        btn_new = QPushButton("Neues Projekt")
        btn_new.setObjectName("newProjectButton")
        btn_new.setIcon(IconManager.get(IconRegistry.ADD, size=16))
        btn_new.setStyleSheet(
            f"""
            #newProjectButton {{
                background: #2563eb;
                color: white;
                border: none;
                border-radius: {dm.RADIUS_MD_PX}px;
                padding: {dm.SPACE_SM_PX}px {dm.SPACE_MD_PX}px;
                font-weight: 500;
            }}
            #newProjectButton:hover {{ background: #1d4ed8; }}
            """
        )
        btn_new.clicked.connect(self._on_new_project)
        btn_row.addWidget(btn_new)
        layout.addLayout(btn_row)

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Projekte filtern…")
        self._filter.textChanged.connect(self._on_filter_changed)
        self._filter.setStyleSheet(
            f"""
            QLineEdit {{
                padding: {dm.SPACE_SM_PX}px {dm.SPACE_MD_PX}px;
                border: 1px solid #e5e7eb;
                border-radius: {dm.RADIUS_MD_PX}px;
                background: white;
            }}
            QLineEdit:focus {{ border-color: #2563eb; }}
            """
        )
        layout.addWidget(self._filter)

        self._table = QTableWidget(0, 3)
        self._table.setObjectName("projectListTable")
        self._table.setHorizontalHeaderLabels(["Projekt", "Status", "Letzter Zugriff"])
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setStyleSheet(
            f"""
            #projectListTable {{
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: {dm.RADIUS_MD_PX}px;
                gridline-color: transparent;
            }}
            #projectListTable::item {{
                padding: {dm.SPACE_SM_PX}px {dm.SPACE_MD_PX}px;
                min-height: {dm.LIST_ITEM_MIN_HEIGHT_PX}px;
            }}
            #projectListTable::item:selected {{
                background: #dbeafe;
                color: #1e3a8a;
            }}
            QHeaderView::section {{
                background: #f8fafc;
                padding: {dm.SPACE_SM_PX}px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: 600;
                font-size: {dm.TEXT_XS_PX}px;
                color: #64748b;
            }}
            """
        )
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self._table, 1)

    def _project_id_for_row(self, row: int) -> int | None:
        it = self._table.item(row, 0)
        if it is None:
            return None
        raw = it.data(Qt.ItemDataRole.UserRole)
        return raw if isinstance(raw, int) else None

    def _on_selection_changed(self) -> None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            self._current_project_id = None
            self._presenter.set_selected_project_id(None)
            self.project_selected.emit(None)
            return
        row = rows[0].row()
        project_id = self._project_id_for_row(row)
        if project_id is not None:
            self._current_project_id = project_id
            self._presenter.set_selected_project_id(project_id)
            self.project_selected.emit(project_id)

    def _on_filter_changed(self, _text: str) -> None:
        self._presenter.set_filter_text(self._filter.text().strip())

    def _on_new_project(self) -> None:
        self.new_project_requested.emit()

    def refresh(self) -> None:
        """Aktualisiert die Projektliste."""
        self._presenter.refresh()

    def set_current(self, project_id: int | None) -> None:
        """Setzt die visuelle Auswahl ohne Signal-Stürme (itemSelectionChanged feuert einmal)."""
        self._current_project_id = project_id
        self._presenter.set_selected_project_id(project_id)
        for r in range(self._table.rowCount()):
            row_project_id = self._project_id_for_row(r)
            if row_project_id == project_id:
                self._table.blockSignals(True)
                self._table.selectRow(r)
                self._table.blockSignals(False)
                return
        self._table.blockSignals(True)
        self._table.clearSelection()
        self._table.blockSignals(False)

    def apply_project_list_loading(self) -> None:
        """Slice 1: bewusst keine sichtbare Loading-Änderung."""

    def apply_project_list_items(
        self,
        items: tuple[ProjectListItem, ...],
        selected_project_id: int | None,
    ) -> None:
        previous_project_id = self._current_project_id
        self._items_by_project_id = {item.project_id: item for item in items}
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        target_row = -1
        for item in items:
            row = self._table.rowCount()
            self._table.insertRow(row)

            col0 = item.display_name
            if item.secondary_text:
                col0 = f"{item.display_name}\n{item.secondary_text}"
            cell0 = QTableWidgetItem(col0)
            cell0.setData(Qt.ItemDataRole.UserRole, item.project_id)
            cell0.setToolTip((item.tooltip_text or col0).replace("\n", " · "))
            self._table.setItem(row, 0, cell0)

            status_text = f"{item.lifecycle_label}\n{item.status_label}"
            cell1 = QTableWidgetItem(status_text)
            cell1.setToolTip(status_text)
            self._table.setItem(row, 1, cell1)

            self._table.setItem(row, 2, QTableWidgetItem(item.last_activity_label))
            if item.project_id == selected_project_id:
                target_row = row

        if target_row >= 0:
            self._table.selectRow(target_row)
        else:
            self._table.clearSelection()
        self._table.blockSignals(False)

        self._current_project_id = selected_project_id
        if previous_project_id == selected_project_id:
            return
        if items and selected_project_id is not None:
            self.project_selected.emit(selected_project_id)
            return
        self.project_selected.emit(None)

    def apply_project_list_empty(self, _reason: str | None) -> None:
        self.apply_project_list_items((), None)

    def apply_project_list_error(self, _message: str | None) -> None:
        self.apply_project_list_items((), None)
