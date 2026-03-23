"""R4: Globale Rollout-Historie, Filter, protokollieren, optional Run-Sprung."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.deployment.models import RolloutListFilter, RolloutOutcome
from app.gui.domains.operations.deployment.dialogs.rollout_record_dialog import RolloutRecordDialog


class RolloutsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._target = QComboBox()
        self._target.addItem("(alle Ziele)", None)
        self._release = QComboBox()
        self._release.addItem("(alle Releases)", None)
        self._outcome = QComboBox()
        self._outcome.addItem("(alle)", None)
        self._outcome.addItem("Erfolg", RolloutOutcome.SUCCESS)
        self._outcome.addItem("Fehlgeschlagen", RolloutOutcome.FAILED)
        self._outcome.addItem("Abgebrochen", RolloutOutcome.CANCELLED)
        self._range = QComboBox()
        self._range.addItem("Alle Zeiten", None)
        self._range.addItem("Letzte 7 Tage", 7)
        self._range.addItem("Letzte 30 Tage", 30)

        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(
            ["Zeit", "Ziel", "Release", "Version", "Ergebnis", "Run-ID", "Nachricht"]
        )
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        apply_b = QPushButton("Filter anwenden")
        apply_b.clicked.connect(self.refresh)
        rec_b = QPushButton("Rollout protokollieren…")
        rec_b.clicked.connect(self._on_record)
        run_b = QPushButton("Zu Workflow-Run…")
        run_b.clicked.connect(self._goto_run)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Ziel:"))
        bar.addWidget(self._target, 1)
        bar.addWidget(QLabel("Release:"))
        bar.addWidget(self._release, 1)
        bar.addWidget(QLabel("Ergebnis:"))
        bar.addWidget(self._outcome)
        bar.addWidget(QLabel("Zeitraum:"))
        bar.addWidget(self._range)
        bar.addWidget(apply_b)
        bar.addWidget(rec_b)
        bar.addWidget(run_b)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(bar)
        root.addWidget(self._table, 1)

    def _reload_filter_combos(self) -> None:
        from app.services import deployment_operations_service as _dep

        svc = _dep.get_deployment_operations_service()
        tid_keep = self._target.currentData()
        rid_keep = self._release.currentData()

        self._target.blockSignals(True)
        self._release.blockSignals(True)
        self._target.clear()
        self._target.addItem("(alle Ziele)", None)
        for t in svc.list_targets():
            self._target.addItem(t.name, t.target_id)
        for i in range(self._target.count()):
            if self._target.itemData(i) == tid_keep:
                self._target.setCurrentIndex(i)
                break
        self._release.clear()
        self._release.addItem("(alle Releases)", None)
        for r in svc.list_releases():
            self._release.addItem(f"{r.display_name} ({r.version_label})", r.release_id)
        for i in range(self._release.count()):
            if self._release.itemData(i) == rid_keep:
                self._release.setCurrentIndex(i)
                break
        self._target.blockSignals(False)
        self._release.blockSignals(False)

    def refresh(self) -> None:
        from app.services import deployment_operations_service as _dep

        self._reload_filter_combos()
        svc = _dep.get_deployment_operations_service()
        since = until = None
        days = self._range.currentData()
        if days is not None:
            now = datetime.now(timezone.utc)
            since_dt = now - timedelta(days=int(days))
            since = since_dt.isoformat()
            until = now.isoformat()
        flt = RolloutListFilter(
            target_id=self._target.currentData(),
            release_id=self._release.currentData(),
            outcome=self._outcome.currentData(),
            since_iso=since,
            until_iso=until,
            limit=800,
        )
        rows = svc.list_rollouts(flt)
        targets = {t.target_id: t.name for t in svc.list_targets()}
        releases = {r.release_id: r for r in svc.list_releases()}
        self._table.setRowCount(0)
        for o in rows:
            row = self._table.rowCount()
            self._table.insertRow(row)
            rel = releases.get(o.release_id)
            rn = rel.display_name if rel else o.release_id
            rv = rel.version_label if rel else ""
            self._table.setItem(row, 0, QTableWidgetItem(o.recorded_at))
            self._table.setItem(row, 1, QTableWidgetItem(targets.get(o.target_id, o.target_id)))
            self._table.setItem(row, 2, QTableWidgetItem(rn))
            self._table.setItem(row, 3, QTableWidgetItem(rv))
            self._table.setItem(row, 4, QTableWidgetItem(o.outcome))
            self._table.setItem(row, 5, QTableWidgetItem(o.workflow_run_id or ""))
            self._table.setItem(row, 6, QTableWidgetItem(o.message or ""))
            self._table.item(row, 5).setData(Qt.ItemDataRole.UserRole, o.workflow_run_id or "")

    def _selected_run_id(self) -> str:
        r = self._table.currentRow()
        if r < 0:
            return ""
        it = self._table.item(r, 5)
        if not it:
            return ""
        return (it.text() or "").strip()

    def _goto_run(self) -> None:
        run_id = self._selected_run_id()
        if not run_id:
            QMessageBox.information(self, "Deployment", "Bitte eine Zeile mit Run-ID wählen.")
            return
        try:
            from app.gui.domains.operations.operations_context import set_pending_context

            set_pending_context({"workflow_ops_run_id": run_id})
        except Exception:
            pass
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea

            host.show_area(NavArea.OPERATIONS, "operations_workflows")

    def _find_workspace_host(self):
        p = self
        while p:
            if hasattr(p, "show_area") and hasattr(p, "_area_to_index"):
                return p
            p = p.parent() if hasattr(p, "parent") else None
        return None

    def _on_record(self) -> None:
        from app.services import deployment_operations_service as _dep

        d = RolloutRecordDialog(self)
        if d.exec() != d.DialogCode.Accepted:
            return
        tid, rid, oc, msg, st, fin, wrid = d.values()
        if not tid or not rid:
            QMessageBox.warning(self, "Deployment", "Ziel und Release sind erforderlich.")
            return
        try:
            _dep.get_deployment_operations_service().record_rollout(
                release_id=rid,
                target_id=tid,
                outcome=oc,
                message=msg or None,
                started_at=st,
                finished_at=fin,
                workflow_run_id=wrid,
                project_id=None,
            )
        except Exception as e:
            QMessageBox.warning(self, "Deployment", str(e))
            return
        self.refresh()
