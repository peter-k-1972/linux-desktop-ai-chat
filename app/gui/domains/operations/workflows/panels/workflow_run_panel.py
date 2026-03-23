"""Runs und NodeRuns — Listenansicht O1 mit schlanken Summaries, Detail via get_run."""

from __future__ import annotations

import json
from typing import Any, List, Optional

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
)

from app.workflows.diagnostics import format_diagnostic_preview, summarize_workflow_run
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.models.run_summary import WorkflowRunSummary
from app.workflows.status import NodeRunStatus, WorkflowRunStatus


def _short_error(msg: Optional[str], max_len: int = 120) -> str:
    if not msg or not str(msg).strip():
        return ""
    s = str(msg).replace("\n", " ").strip()
    return s if len(s) <= max_len else s[: max_len - 1] + "…"


class WorkflowRunPanel(QFrame):
    """Run-Liste (Summaries), NodeRun-Liste und Detail (nach get_run)."""

    refresh_requested = Signal()
    test_run_requested = Signal()
    rerun_requested = Signal()
    run_selection_changed = Signal(object)  # Optional[str] run_id
    node_run_selection_changed = Signal(object)  # Optional[str] node_id
    jump_to_node_requested = Signal(str)
    scope_or_filter_changed = Signal()

    RUN_SCOPE_WORKFLOW = "workflow"
    RUN_SCOPE_PROJECT = "project"
    RUN_SCOPE_ALL = "all"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("workflowRunPanel")
        self._wf_id: Optional[str] = None
        self._summaries: List[WorkflowRunSummary] = []
        self._selected_run: Optional[WorkflowRun] = None
        self._jump_context_workflow_id: Optional[str] = None
        self._suppress_node_run_emit = False
        self._suppress_run_emit = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(QLabel("Ausführungen & NodeRuns"))

        self._scope_caption = QLabel()
        self._scope_caption.setObjectName("workflowRunsScopeCaption")
        self._scope_caption.setWordWrap(True)
        self._scope_caption.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(self._scope_caption)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Run-Liste:"))
        self._scope_combo = QComboBox()
        self._scope_combo.addItem("Dieser Workflow", self.RUN_SCOPE_WORKFLOW)
        self._scope_combo.addItem("Aktives Projekt", self.RUN_SCOPE_PROJECT)
        self._scope_combo.addItem("Alle Runs", self.RUN_SCOPE_ALL)
        self._scope_combo.setCurrentIndex(0)
        self._scope_combo.currentIndexChanged.connect(lambda _i: self.scope_or_filter_changed.emit())
        filter_row.addWidget(self._scope_combo)
        filter_row.addWidget(QLabel("Status:"))
        self._status_combo = QComboBox()
        self._status_combo.addItem("Alle", None)
        for st in WorkflowRunStatus:
            self._status_combo.addItem(st.value, st.value)
        self._status_combo.currentIndexChanged.connect(lambda _i: self.scope_or_filter_changed.emit())
        filter_row.addWidget(self._status_combo)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        self._runs_empty_hint = QLabel("")
        self._runs_empty_hint.setObjectName("workflowRunsEmptyHint")
        self._runs_empty_hint.setWordWrap(True)
        self._runs_empty_hint.setVisible(False)
        layout.addWidget(self._runs_empty_hint)

        btn_row = QHBoxLayout()
        self._btn_refresh = QPushButton("Runs aktualisieren")
        self._btn_refresh.clicked.connect(self.refresh_requested.emit)
        self._btn_run = QPushButton("Test-Run …")
        self._btn_run.clicked.connect(self.test_run_requested.emit)
        self._btn_jump = QPushButton("Knoten im Editor wählen")
        self._btn_jump.clicked.connect(self._on_jump_clicked)
        self._btn_jump.setEnabled(False)
        self._btn_rerun = QPushButton("Erneut ausführen …")
        self._btn_rerun.setToolTip(
            "Startet einen neuen Run mit derselben Workflow-ID und den Eingaben aus dem Dialog "
            "(Voreinstellung: initial_input dieses Laufs)."
        )
        self._btn_rerun.setEnabled(False)
        self._btn_rerun.clicked.connect(self._on_rerun_clicked)
        btn_row.addWidget(self._btn_refresh)
        btn_row.addWidget(self._btn_run)
        btn_row.addWidget(self._btn_rerun)
        btn_row.addWidget(self._btn_jump)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        split = QSplitter(Qt.Orientation.Vertical)

        self._runs_table = QTableWidget(0, 10)
        self._runs_table.setHorizontalHeaderLabels(
            [
                "run_id",
                "workflow_id",
                "workflow_name",
                "project_id",
                "version",
                "Status",
                "created_at",
                "started_at",
                "finished_at",
                "error",
            ]
        )
        self._runs_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._runs_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._runs_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._runs_table.verticalHeader().setVisible(False)
        self._runs_table.itemSelectionChanged.connect(self._on_run_sel_changed)
        self._runs_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._runs_table.customContextMenuRequested.connect(self._on_runs_table_context_menu)
        split.addWidget(self._runs_table)

        self._node_table = QTableWidget(0, 7)
        self._node_table.setHorizontalHeaderLabels(
            [
                "node_run_id",
                "node_id",
                "node_type",
                "Status",
                "started_at",
                "finished_at",
                "retry",
            ]
        )
        self._node_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._node_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._node_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._node_table.verticalHeader().setVisible(False)
        self._node_table.itemSelectionChanged.connect(self._on_node_run_sel_changed)
        self._node_table.itemDoubleClicked.connect(self._on_node_run_double_clicked)
        split.addWidget(self._node_table)

        detail = QFrame()
        dv = QVBoxLayout(detail)
        dv.setContentsMargins(0, 4, 0, 0)
        dv.addWidget(QLabel("Diagnose (aus gespeicherten Lauf-Daten)"))
        self._diag_frame = QFrame()
        self._diag_frame.setObjectName("workflowRunDiagnosisFrame")
        self._diag_frame.setStyleSheet(
            """
            #workflowRunDiagnosisFrame {
                background: rgba(148, 163, 184, 0.08);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                padding: 8px;
            }
            """
        )
        dvl = QVBoxLayout(self._diag_frame)
        dvl.setSpacing(6)
        self._diag_headline = QLabel("—")
        self._diag_headline.setWordWrap(True)
        self._diag_headline.setStyleSheet("font-weight: 600; font-size: 13px; color: #e2e8f0;")
        dvl.addWidget(self._diag_headline)
        self._diag_summary = QLabel("—")
        self._diag_summary.setWordWrap(True)
        self._diag_summary.setStyleSheet("color: #cbd5e1; font-size: 12px;")
        dvl.addWidget(self._diag_summary)
        self._diag_detail = QLabel("—")
        self._diag_detail.setWordWrap(True)
        self._diag_detail.setStyleSheet("color: #94a3b8; font-size: 11px;")
        dvl.addWidget(self._diag_detail)
        self._diag_snapshot = QLabel(
            "Hinweis: Definition und Eingaben im unteren Bereich sind Snapshot zum Laufzeitpunkt (read-only)."
        )
        self._diag_snapshot.setWordWrap(True)
        self._diag_snapshot.setStyleSheet("color: #64748b; font-size: 10px;")
        dvl.addWidget(self._diag_snapshot)
        dv.addWidget(self._diag_frame)

        dv.addWidget(
            QLabel("Run-Rohdaten (Metadaten, Run-Fehlermeldung, Ein-/Ausgabe)")
        )
        self._run_summary = QTextEdit()
        self._run_summary.setReadOnly(True)
        self._run_summary.setMaximumHeight(120)
        dv.addWidget(self._run_summary)

        dv.addWidget(QLabel("NodeRun-Rohdaten (Zeile in der NodeRun-Tabelle wählen)"))
        tabs = QTabWidget()
        self._tab_input = QTextEdit()
        self._tab_input.setReadOnly(True)
        self._tab_output = QTextEdit()
        self._tab_output.setReadOnly(True)
        self._tab_error = QTextEdit()
        self._tab_error.setReadOnly(True)
        tabs.addTab(self._tab_input, "Input")
        tabs.addTab(self._tab_output, "Output")
        tabs.addTab(self._tab_error, "Fehler (Knoten)")
        dv.addWidget(tabs, 1)
        split.addWidget(detail)

        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 2)
        split.setStretchFactor(2, 3)
        layout.addWidget(split, 1)

    def run_list_scope(self) -> str:
        v = self._scope_combo.currentData()
        return str(v) if v else self.RUN_SCOPE_WORKFLOW

    def status_filter_value(self) -> Optional[str]:
        return self._status_combo.currentData()

    def set_run_list_scope(self, scope: str, *, silent: bool = False) -> None:
        """Scope setzen. ``silent=True`` unterdrückt ``scope_or_filter_changed`` (O4: ein Refresh außen)."""
        for i in range(self._scope_combo.count()):
            if self._scope_combo.itemData(i) == scope:
                if silent:
                    self._scope_combo.blockSignals(True)
                self._scope_combo.setCurrentIndex(i)
                if silent:
                    self._scope_combo.blockSignals(False)
                return

    def set_jump_context_workflow_id(self, workflow_id: Optional[str]) -> None:
        """Workflow im Editor — Steuerung „Knoten wählen“ nur bei passendem Run."""
        self._jump_context_workflow_id = workflow_id

    def set_workflow_id(self, workflow_id: Optional[str]) -> None:
        self._wf_id = workflow_id
        self._suppress_run_emit = True
        self._suppress_node_run_emit = True
        self._runs_table.setRowCount(0)
        self._node_table.setRowCount(0)
        self._summaries = []
        self._selected_run = None
        self._clear_details()
        self._suppress_node_run_emit = False
        self._suppress_run_emit = False
        self._btn_jump.setEnabled(False)
        self._btn_rerun.setEnabled(False)
        self._runs_empty_hint.setVisible(False)
        self._scope_caption.setText("")
        self.run_selection_changed.emit(None)
        self.node_run_selection_changed.emit(None)

    def set_run_summaries(
        self,
        summaries: List[WorkflowRunSummary],
        *,
        scope_caption: str,
        empty_hint: str,
    ) -> None:
        self._summaries = list(summaries)
        self._scope_caption.setText(scope_caption)
        self._runs_empty_hint.setText(empty_hint)
        self._suppress_run_emit = True
        self._runs_table.blockSignals(True)
        self._runs_table.setRowCount(0)
        for s in summaries:
            row = self._runs_table.rowCount()
            self._runs_table.insertRow(row)
            it0 = QTableWidgetItem(s.run_id)
            it0.setData(Qt.ItemDataRole.UserRole, s.run_id)
            self._runs_table.setItem(row, 0, it0)
            self._runs_table.setItem(row, 1, QTableWidgetItem(s.workflow_id))
            self._runs_table.setItem(row, 2, QTableWidgetItem(s.workflow_name))
            pid_txt = "—" if s.project_id is None else str(s.project_id)
            self._runs_table.setItem(row, 3, QTableWidgetItem(pid_txt))
            self._runs_table.setItem(row, 4, QTableWidgetItem(str(s.workflow_version)))
            self._runs_table.setItem(row, 5, QTableWidgetItem(s.status))
            self._runs_table.setItem(row, 6, QTableWidgetItem(_fmt_dt(s.created_at)))
            self._runs_table.setItem(row, 7, QTableWidgetItem(_fmt_dt(s.started_at)))
            self._runs_table.setItem(row, 8, QTableWidgetItem(_fmt_dt(s.finished_at)))
            self._runs_table.setItem(row, 9, QTableWidgetItem(_short_error(s.error_message)))
        self._runs_table.resizeColumnsToContents()
        self._runs_table.blockSignals(False)
        self._suppress_run_emit = False
        self._selected_run = None
        self._populate_node_table(None)
        self._clear_details()
        self._runs_empty_hint.setVisible(len(summaries) == 0 and bool(empty_hint.strip()))
        self._btn_jump.setEnabled(False)
        self._btn_rerun.setEnabled(False)
        self.run_selection_changed.emit(None)
        self.node_run_selection_changed.emit(None)

    def set_full_run_detail(self, run: WorkflowRun) -> None:
        """Nach get_run(run_id): NodeRuns und Zusammenfassung füllen."""
        self._selected_run = run
        self._populate_node_table(run)
        self._apply_diagnosis(run)
        self._fill_run_summary(run)
        self._select_first_failed_node_if_any()
        self._update_rerun_enabled()

    def clear_full_run_detail(self) -> None:
        self._selected_run = None
        self._populate_node_table(None)
        self._clear_details()
        self._btn_jump.setEnabled(False)
        self._btn_rerun.setEnabled(False)
        self.node_run_selection_changed.emit(None)

    def select_run_by_id(self, run_id: str) -> None:
        """Programmatische Auswahl (z. B. nach Test-Run)."""
        for row in range(self._runs_table.rowCount()):
            it = self._runs_table.item(row, 0)
            if it and it.data(Qt.ItemDataRole.UserRole) == run_id:
                self._suppress_run_emit = True
                self._runs_table.selectRow(row)
                self._suppress_run_emit = False
                self._apply_run_selection_by_row(row)
                return

    def current_run(self) -> Optional[WorkflowRun]:
        return self._selected_run

    def selected_node_run(self) -> Optional[NodeRun]:
        rows = self._node_table.selectionModel().selectedRows()
        if not rows or not self._selected_run:
            return None
        row = rows[0].row()
        if row < 0 or row >= len(self._selected_run.node_runs):
            return None
        return self._selected_run.node_runs[row]

    def sync_node_run_selection_to_node_id(self, node_id: Optional[str]) -> None:
        """Canvas/Tabellen-Selektion → NodeRun-Zeile (ohne jump-Signal)."""
        self._suppress_node_run_emit = True
        if not node_id or not self._selected_run:
            self._node_table.clearSelection()
            self._suppress_node_run_emit = False
            self._fill_node_run_detail(None)
            return
        for i, nr in enumerate(self._selected_run.node_runs):
            if nr.node_id == node_id:
                self._node_table.selectRow(i)
                self._suppress_node_run_emit = False
                self._fill_node_run_detail(nr)
                return
        self._node_table.clearSelection()
        self._suppress_node_run_emit = False
        self._fill_node_run_detail(None)

    def _jump_allowed_for_current_run(self) -> bool:
        if not self._selected_run or not self._jump_context_workflow_id:
            return False
        return self._selected_run.workflow_id == self._jump_context_workflow_id

    def _can_rerun(self) -> bool:
        if not self._selected_run:
            return False
        return bool((self._selected_run.workflow_id or "").strip())

    def _update_rerun_enabled(self) -> None:
        self._btn_rerun.setEnabled(self._can_rerun())

    def _on_rerun_clicked(self) -> None:
        if self._can_rerun():
            self.rerun_requested.emit()

    def _on_runs_table_context_menu(self, pos: QPoint) -> None:
        if not self._can_rerun():
            return
        menu = QMenu(self)
        act = menu.addAction("Erneut ausführen …")
        act.triggered.connect(self.rerun_requested.emit)
        menu.exec(self._runs_table.viewport().mapToGlobal(pos))

    def _on_run_sel_changed(self) -> None:
        if self._suppress_run_emit:
            return
        rows = self._runs_table.selectionModel().selectedRows()
        if not rows:
            self._apply_run_selection_by_row(-1)
            return
        self._apply_run_selection_by_row(rows[0].row())

    def _apply_run_selection_by_row(self, row: int) -> None:
        if row < 0 or row >= len(self._summaries):
            self.clear_full_run_detail()
            self.run_selection_changed.emit(None)
            return
        rid = self._summaries[row].run_id
        self.clear_full_run_detail()
        self.run_selection_changed.emit(rid)

    def _populate_node_table(self, run: Optional[WorkflowRun]) -> None:
        self._suppress_node_run_emit = True
        self._node_table.setRowCount(0)
        if not run:
            self._suppress_node_run_emit = False
            return
        for nr in run.node_runs:
            r = self._node_table.rowCount()
            self._node_table.insertRow(r)
            self._node_table.setItem(r, 0, QTableWidgetItem(nr.node_run_id))
            self._node_table.setItem(r, 1, QTableWidgetItem(nr.node_id))
            self._node_table.setItem(r, 2, QTableWidgetItem(nr.node_type))
            self._node_table.setItem(r, 3, QTableWidgetItem(nr.status.value))
            self._node_table.setItem(r, 4, QTableWidgetItem(_fmt_dt(nr.started_at)))
            self._node_table.setItem(r, 5, QTableWidgetItem(_fmt_dt(nr.finished_at)))
            self._node_table.setItem(r, 6, QTableWidgetItem(str(nr.retry_count)))
        self._node_table.resizeColumnsToContents()
        self._suppress_node_run_emit = False

    def _on_node_run_sel_changed(self) -> None:
        if self._suppress_node_run_emit:
            return
        nr = self.selected_node_run()
        self._fill_node_run_detail(nr)
        self._btn_jump.setEnabled(
            nr is not None and self._jump_allowed_for_current_run()
        )
        self.node_run_selection_changed.emit(nr.node_id if nr else None)

    def _on_node_run_double_clicked(self, item: QTableWidgetItem) -> None:
        row = item.row()
        if not self._selected_run or row < 0 or row >= len(self._selected_run.node_runs):
            return
        if not self._jump_allowed_for_current_run():
            return
        self.jump_to_node_requested.emit(self._selected_run.node_runs[row].node_id)

    def _on_jump_clicked(self) -> None:
        nr = self.selected_node_run()
        if nr and self._jump_allowed_for_current_run():
            self.jump_to_node_requested.emit(nr.node_id)

    def _clear_details(self) -> None:
        self._clear_diagnosis()
        self._run_summary.clear()
        self._clear_node_tabs()

    def _clear_diagnosis(self) -> None:
        self._diag_headline.setText("—")
        self._diag_summary.setText("—")
        self._diag_detail.setText("—")
        self._diag_frame.setToolTip("")

    def _apply_diagnosis(self, run: WorkflowRun) -> None:
        d = summarize_workflow_run(run)
        self._diag_headline.setText(d.headline)
        self._diag_summary.setText(d.summary)
        parts: list[str] = [f"Run-Status: {run.status.value}"]
        if d.run_error:
            parts.append(f"Run-Fehler (Vorschau): {format_diagnostic_preview(d.run_error)}")
        else:
            parts.append("Run-Fehler (Ebene Run): —")
        if d.failed_node_id:
            parts.append(
                f"Fehler-Knoten: {d.failed_node_id} (Typ: {d.failed_node_type or '—'})"
            )
            if d.failed_node_error_short:
                parts.append(f"Knoten-Fehler (Kurz): {d.failed_node_error_short}")
        elif d.is_failed and not d.failed_node_id:
            parts.append("Kein Knoten mit Status „failed“ in den gespeicherten NodeRuns.")
        self._diag_detail.setText("\n".join(parts))
        tip_chunks: list[str] = []
        if d.run_error:
            tip_chunks.append(f"Run-Fehler (voll):\n{d.run_error}")
        if d.failed_node_error:
            tip_chunks.append(f"Knoten-Fehler (voll):\n{d.failed_node_error}")
        self._diag_frame.setToolTip("\n\n".join(tip_chunks) if tip_chunks else "")

    def _select_first_failed_node_if_any(self) -> None:
        run = self._selected_run
        if not run:
            self._btn_jump.setEnabled(False)
            return
        if run.status != WorkflowRunStatus.FAILED:
            self._clear_node_tabs()
            self._tab_error.setToolTip("")
            self._btn_jump.setEnabled(False)
            self.node_run_selection_changed.emit(None)
            return
        for i, nr in enumerate(run.node_runs):
            if nr.status == NodeRunStatus.FAILED:
                self._suppress_node_run_emit = True
                self._node_table.selectRow(i)
                self._suppress_node_run_emit = False
                self._fill_node_run_detail(nr)
                self._btn_jump.setEnabled(self._jump_allowed_for_current_run())
                self.node_run_selection_changed.emit(nr.node_id)
                return
        self._clear_node_tabs()
        self._tab_error.setToolTip("")
        self._btn_jump.setEnabled(False)
        self.node_run_selection_changed.emit(None)

    def _clear_node_tabs(self) -> None:
        self._tab_input.setPlainText("—")
        self._tab_output.setPlainText("—")
        self._tab_error.setPlainText("—")
        self._tab_error.setToolTip("")

    def _fill_run_summary(self, run: WorkflowRun) -> None:
        lines = [
            f"run_id: {run.run_id}",
            f"workflow_id: {run.workflow_id}",
            f"workflow_version: {run.workflow_version}",
            f"status: {run.status.value}",
            f"created_at: {_fmt_dt(run.created_at)}",
            f"started_at: {_fmt_dt(run.started_at)}",
            f"finished_at: {_fmt_dt(run.finished_at)}",
            "",
            f"error_message: {run.error_message or '—'}",
            "",
            "initial_input:",
            _fmt_json(run.initial_input),
            "",
            "final_output:",
            _fmt_json(run.final_output),
        ]
        self._run_summary.setPlainText("\n".join(lines))

    def _fill_node_run_detail(self, nr: Optional[NodeRun]) -> None:
        if not nr:
            self._clear_node_tabs()
            return
        self._tab_input.setPlainText(_fmt_json(nr.input_payload))
        self._tab_output.setPlainText(_fmt_json(nr.output_payload))
        err = (nr.error_message or "").strip() or "—"
        self._tab_error.setPlainText(err)
        raw = (nr.error_message or "").strip()
        self._tab_error.setToolTip(raw if len(raw) > 120 else "")


def _fmt_dt(dt: Any) -> str:
    if dt is None:
        return ""
    return dt.isoformat()


def _fmt_json(data: Any) -> str:
    if data is None:
        return "—"
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return repr(data)
