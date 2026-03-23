"""R3: Geplante Workflow-Ausführungen in Operations / Workflows."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.workflows.scheduling.models import ScheduleListRow


def _format_local_hint(utc_iso: str) -> str:
    try:
        s = (utc_iso or "").strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M %Z")
    except ValueError:
        return utc_iso or "—"


class WorkflowSchedulePanel(QFrame):
    """Liste und Aktionen; Fachlogik nur über Callbacks/Services außerhalb."""

    refresh_requested = Signal()
    new_requested = Signal()
    edit_requested = Signal(str)
    delete_requested = Signal(str)
    toggle_enabled_requested = Signal(str, bool)
    run_now_requested = Signal(str)
    jump_to_run_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("workflowSchedulePanel")
        self._rows: List[ScheduleListRow] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(QLabel("Geplante Ausführungen"))

        self._table = QTableWidget(0, 6)
        self._table.setObjectName("workflowScheduleTable")
        self._table.setHorizontalHeaderLabels(
            ["workflow_id", "Name", "next_run_at (UTC)", "lokal", "aktiv", "letzter Run"]
        )
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.itemSelectionChanged.connect(self._sync_selection)
        layout.addWidget(self._table, 1)

        btn_row = QHBoxLayout()
        self._btn_refresh = QPushButton("Aktualisieren")
        self._btn_refresh.clicked.connect(self.refresh_requested.emit)
        btn_row.addWidget(self._btn_refresh)
        self._btn_new = QPushButton("Anlegen…")
        self._btn_new.clicked.connect(self.new_requested.emit)
        btn_row.addWidget(self._btn_new)
        self._btn_edit = QPushButton("Bearbeiten…")
        self._btn_edit.clicked.connect(self._emit_edit)
        btn_row.addWidget(self._btn_edit)
        self._btn_toggle = QPushButton("Aktivieren/Deaktivieren")
        self._btn_toggle.clicked.connect(self._emit_toggle)
        btn_row.addWidget(self._btn_toggle)
        self._btn_run = QPushButton("Jetzt ausführen")
        self._btn_run.clicked.connect(self._emit_run_now)
        btn_row.addWidget(self._btn_run)
        self._btn_jump = QPushButton("Zum letzten Run")
        self._btn_jump.clicked.connect(self._emit_jump)
        btn_row.addWidget(self._btn_jump)
        self._btn_del = QPushButton("Löschen")
        self._btn_del.clicked.connect(self._emit_delete)
        btn_row.addWidget(self._btn_del)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._detail = QLabel("")
        self._detail.setObjectName("workflowScheduleDetail")
        self._detail.setWordWrap(True)
        self._detail.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(self._detail)

        self._get_last_run_id: Optional[Callable[[str], Optional[str]]] = None
        self._apply_buttons_state()

    def set_last_run_resolver(self, fn: Optional[Callable[[str], Optional[str]]]) -> None:
        """Optional: schedule_id -> letzte run_id aus Log."""
        self._get_last_run_id = fn

    def set_schedules(self, rows: List[ScheduleListRow]) -> None:
        self._rows = list(rows)
        self._table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            s = r.schedule
            last_run = ""
            if self._get_last_run_id:
                try:
                    rid = self._get_last_run_id(s.schedule_id)
                    last_run = rid or ""
                except Exception:
                    last_run = ""
            self._table.setItem(i, 0, QTableWidgetItem(s.workflow_id))
            self._table.setItem(i, 1, QTableWidgetItem(r.workflow_name or "—"))
            self._table.setItem(i, 2, QTableWidgetItem(s.next_run_at))
            self._table.setItem(i, 3, QTableWidgetItem(_format_local_hint(s.next_run_at)))
            self._table.setItem(i, 4, QTableWidgetItem("ja" if s.enabled else "nein"))
            self._table.setItem(i, 5, QTableWidgetItem(last_run))
            it0 = self._table.item(i, 0)
            if it0 is not None:
                it0.setData(Qt.ItemDataRole.UserRole, s.schedule_id)
        self._apply_buttons_state()

    def selected_schedule_id(self) -> Optional[str]:
        r = self._table.currentRow()
        if r < 0 or r >= self._table.rowCount():
            return None
        it = self._table.item(r, 0)
        if it is None:
            return None
        sid = it.data(Qt.ItemDataRole.UserRole)
        return sid if isinstance(sid, str) else None

    def _sync_selection(self) -> None:
        sid = self.selected_schedule_id()
        if not sid:
            self._detail.setText("")
            self._apply_buttons_state()
            return
        row = next((x for x in self._rows if x.schedule.schedule_id == sid), None)
        if row:
            s = row.schedule
            self._detail.setText(
                f"schedule_id={s.schedule_id} · rule_json={s.rule_json} · "
                f"last_fired_at={s.last_fired_at or '—'}"
            )
        self._apply_buttons_state()

    def _apply_buttons_state(self) -> None:
        has = self.selected_schedule_id() is not None
        self._btn_edit.setEnabled(has)
        self._btn_toggle.setEnabled(has)
        self._btn_run.setEnabled(has)
        self._btn_del.setEnabled(has)
        can_jump = False
        sid = self.selected_schedule_id()
        if sid and self._get_last_run_id:
            try:
                can_jump = bool(self._get_last_run_id(sid))
            except Exception:
                can_jump = False
        self._btn_jump.setEnabled(can_jump)

    def _emit_edit(self) -> None:
        sid = self.selected_schedule_id()
        if sid:
            self.edit_requested.emit(sid)

    def _emit_toggle(self) -> None:
        sid = self.selected_schedule_id()
        if not sid:
            return
        row = next((x for x in self._rows if x.schedule.schedule_id == sid), None)
        if row:
            self.toggle_enabled_requested.emit(sid, not row.schedule.enabled)

    def _emit_run_now(self) -> None:
        sid = self.selected_schedule_id()
        if sid:
            self.run_now_requested.emit(sid)

    def _emit_jump(self) -> None:
        sid = self.selected_schedule_id()
        if not sid or not self._get_last_run_id:
            return
        rid = self._get_last_run_id(sid)
        if rid:
            self.jump_to_run_requested.emit(rid)

    def _emit_delete(self) -> None:
        sid = self.selected_schedule_id()
        if sid:
            self.delete_requested.emit(sid)
