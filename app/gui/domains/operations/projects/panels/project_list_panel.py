"""
ProjectListPanel – Projektarchiv-Liste (Projekte, Status, letzter Zugriff).
"""

from datetime import datetime

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

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.shared.layout_constants import SIDEBAR_PADDING, WIDGET_SPACING
from app.gui.theme import design_metrics as dm
from app.projects.lifecycle import lifecycle_label_de


def _format_last_access(ts: str | None) -> str:
    if not ts:
        return "—"
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(ts) if ts else "—"


def _project_recency_key(p: dict):
    for key in ("updated_at", "created_at"):
        v = p.get(key)
        if v:
            try:
                return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
            except Exception:
                continue
    return datetime.min


class ProjectListPanel(QFrame):
    """Panel für Projektliste. Links im Projects-Workspace."""

    project_selected = Signal(object)  # project dict or None
    new_project_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectListPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(380)
        self._current_project_id = None
        self._setup_ui()
        self._load_projects()

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

    def _project_for_row(self, row: int) -> dict | None:
        it = self._table.item(row, 0)
        if it is None:
            return None
        p = it.data(Qt.ItemDataRole.UserRole)
        return p if isinstance(p, dict) else None

    def _on_selection_changed(self) -> None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            self._current_project_id = None
            self.project_selected.emit(None)
            return
        row = rows[0].row()
        proj = self._project_for_row(row)
        if proj is not None:
            self._current_project_id = proj.get("project_id")
            self.project_selected.emit(proj)

    def _load_projects(self) -> None:
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        try:
            from app.services.project_service import get_project_service

            svc = get_project_service()
            filter_text = self._filter.text().strip()
            projects = list(svc.list_projects(filter_text))
            projects.sort(key=_project_recency_key, reverse=True)

            target_row = -1
            for i, proj in enumerate(projects):
                pid = proj.get("project_id")
                name = proj.get("name", "Projekt")
                sub = (proj.get("internal_code") or "").strip() or (
                    proj.get("customer_name") or ""
                ).strip()
                col0 = f"{name}\n{sub}" if sub else name

                lifecycle = (proj.get("lifecycle_status") or "active").strip().lower()
                tech = (proj.get("status") or "active").strip()
                status_text = f"{lifecycle_label_de(lifecycle)}\n{tech}"

                last = _format_last_access(proj.get("updated_at") or proj.get("created_at"))

                r = self._table.rowCount()
                self._table.insertRow(r)

                c0 = QTableWidgetItem(col0)
                c0.setData(Qt.ItemDataRole.UserRole, proj)
                c0.setToolTip(col0.replace("\n", " · "))
                self._table.setItem(r, 0, c0)

                c1 = QTableWidgetItem(status_text)
                c1.setToolTip(status_text)
                self._table.setItem(r, 1, c1)

                c2 = QTableWidgetItem(last)
                self._table.setItem(r, 2, c2)

                if self._current_project_id is not None and pid == self._current_project_id:
                    target_row = r

            if target_row >= 0:
                self._table.selectRow(target_row)
            elif self._table.rowCount() == 0:
                self._current_project_id = None
                self.project_selected.emit(None)
            elif self._current_project_id is None:
                self._table.selectRow(0)
                p0 = self._project_for_row(0)
                if p0:
                    self._current_project_id = p0.get("project_id")
                    self.project_selected.emit(p0)
            else:
                self._table.clearSelection()
                self.project_selected.emit(None)
        except Exception:
            pass
        finally:
            self._table.blockSignals(False)

    def _on_filter_changed(self, _text: str) -> None:
        self._load_projects()

    def _on_new_project(self) -> None:
        self.new_project_requested.emit()

    def refresh(self) -> None:
        """Aktualisiert die Projektliste."""
        self._load_projects()

    def set_current(self, project_id: int | None) -> None:
        """Setzt die visuelle Auswahl ohne Signal-Stürme (itemSelectionChanged feuert einmal)."""
        self._current_project_id = project_id
        for r in range(self._table.rowCount()):
            proj = self._project_for_row(r)
            if proj and proj.get("project_id") == project_id:
                self._table.blockSignals(True)
                self._table.selectRow(r)
                self._table.blockSignals(False)
                return
        self._table.blockSignals(True)
        self._table.clearSelection()
        self._table.blockSignals(False)
