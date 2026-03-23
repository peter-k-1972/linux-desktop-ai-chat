"""R4: Releases — Liste, Detail, Rollout-Historie pro Release, Bearbeiten/Archivieren."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.deployment.models import RolloutListFilter
from app.gui.domains.operations.deployment.dialogs.release_edit_dialog import ReleaseEditDialog


class ReleasesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._list = QTableWidget()
        self._list.setColumnCount(5)
        self._list.setHorizontalHeaderLabels(
            ["Name", "Version", "Lifecycle", "Artefakt", "Projekt-ID"]
        )
        self._list.setAlternatingRowColors(True)
        self._list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._list.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._list.itemSelectionChanged.connect(self._on_sel)

        self._detail = QLabel("")
        self._detail.setWordWrap(True)
        self._detail.setTextFormat(Qt.TextFormat.RichText)
        self._detail.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)

        self._hist = QTableWidget()
        self._hist.setColumnCount(5)
        self._hist.setHorizontalHeaderLabels(
            ["Zeit", "Ziel", "Ergebnis", "Run-ID", "Nachricht"]
        )
        self._hist.setAlternatingRowColors(True)
        self._hist.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._hist.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        new_b = QPushButton("Neu…")
        new_b.clicked.connect(self._on_new)
        edit_b = QPushButton("Bearbeiten…")
        edit_b.clicked.connect(self._on_edit)
        arch_b = QPushButton("Archivieren")
        arch_b.clicked.connect(self._on_archive)
        ref_b = QPushButton("Aktualisieren")
        ref_b.clicked.connect(self.refresh)

        bar = QHBoxLayout()
        bar.addWidget(new_b)
        bar.addWidget(edit_b)
        bar.addWidget(arch_b)
        bar.addStretch(1)
        bar.addWidget(ref_b)

        bottom = QSplitter(Qt.Orientation.Vertical)
        bottom.addWidget(self._detail)
        bottom.addWidget(self._hist)
        bottom.setStretchFactor(0, 0)
        bottom.setStretchFactor(1, 1)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.addWidget(self._list)
        split.addWidget(bottom)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 1)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(bar)
        root.addWidget(split, 1)

    def refresh(self) -> None:
        from app.services import deployment_operations_service as _dep

        svc = _dep.get_deployment_operations_service()
        rows = svc.list_releases()
        self._list.setRowCount(0)
        for r in rows:
            row = self._list.rowCount()
            self._list.insertRow(row)
            self._list.setItem(row, 0, QTableWidgetItem(r.display_name))
            self._list.setItem(row, 1, QTableWidgetItem(r.version_label))
            self._list.setItem(row, 2, QTableWidgetItem(r.lifecycle_status))
            self._list.setItem(row, 3, QTableWidgetItem(r.artifact_kind or ""))
            self._list.setItem(
                row, 4, QTableWidgetItem("" if r.project_id is None else str(r.project_id))
            )
            self._list.item(row, 0).setData(Qt.ItemDataRole.UserRole, r.release_id)
        self._on_sel()

    def _selected_release_id(self) -> str | None:
        r = self._list.currentRow()
        if r < 0:
            return None
        it = self._list.item(r, 0)
        if not it:
            return None
        return it.data(Qt.ItemDataRole.UserRole)

    def _on_sel(self) -> None:
        from app.services import deployment_operations_service as _dep

        rid = self._selected_release_id()
        if not rid:
            self._detail.setText("")
            self._hist.setRowCount(0)
            return
        svc = _dep.get_deployment_operations_service()
        rel = svc.get_release(rid)
        if not rel:
            self._detail.setText("")
            self._hist.setRowCount(0)
            return
        self._detail.setText(
            f"<b>{rel.display_name}</b> {rel.version_label}<br/>"
            f"Lifecycle: {rel.lifecycle_status}<br/>"
            f"Referenz: {rel.artifact_ref or '—'}<br/>"
            f"Art: {rel.artifact_kind or '—'}"
        )
        rollouts = svc.list_rollouts(RolloutListFilter(release_id=rid, limit=200))
        targets = {t.target_id: t.name for t in svc.list_targets()}
        self._hist.setRowCount(0)
        for o in rollouts:
            row = self._hist.rowCount()
            self._hist.insertRow(row)
            self._hist.setItem(row, 0, QTableWidgetItem(o.recorded_at))
            self._hist.setItem(row, 1, QTableWidgetItem(targets.get(o.target_id, o.target_id)))
            self._hist.setItem(row, 2, QTableWidgetItem(o.outcome))
            self._hist.setItem(row, 3, QTableWidgetItem(o.workflow_run_id or ""))
            self._hist.setItem(row, 4, QTableWidgetItem(o.message or ""))
            if o.workflow_run_id:
                self._hist.item(row, 3).setData(Qt.ItemDataRole.UserRole, o.workflow_run_id)

    def _on_new(self) -> None:
        from app.services import deployment_operations_service as _dep

        d = ReleaseEditDialog(self, title="Release anlegen", initial=None, allow_lifecycle=False)
        if d.exec() != d.DialogCode.Accepted:
            return
        dn, vl, ak, ar, _lc, pid = d.values()
        try:
            _dep.get_deployment_operations_service().create_release(
                display_name=dn,
                version_label=vl,
                artifact_kind=ak,
                artifact_ref=ar,
                project_id=pid,
            )
        except Exception as e:
            QMessageBox.warning(self, "Deployment", str(e))
            return
        self.refresh()

    def _on_edit(self) -> None:
        rid = self._selected_release_id()
        if not rid:
            QMessageBox.information(self, "Deployment", "Bitte ein Release wählen.")
            return
        from app.services import deployment_operations_service as _dep

        svc = _dep.get_deployment_operations_service()
        rel = svc.get_release(rid)
        if not rel:
            QMessageBox.warning(self, "Deployment", "Release nicht gefunden.")
            return
        d = ReleaseEditDialog(self, title="Release bearbeiten", initial=rel, allow_lifecycle=True)
        if d.exec() != d.DialogCode.Accepted:
            return
        dn, vl, ak, ar, lc, pid = d.values()
        try:
            if lc is None:
                lc = rel.lifecycle_status
            svc.update_release(
                release_id=rid,
                display_name=dn,
                version_label=vl,
                artifact_kind=ak,
                artifact_ref=ar,
                lifecycle_status=lc,
                project_id=pid,
            )
        except Exception as e:
            QMessageBox.warning(self, "Deployment", str(e))
            return
        self.refresh()

    def _on_archive(self) -> None:
        rid = self._selected_release_id()
        if not rid:
            QMessageBox.information(self, "Deployment", "Bitte ein Release wählen.")
            return
        if QMessageBox.question(
            self,
            "Deployment",
            "Release wirklich archivieren?",
        ) != QMessageBox.StandardButton.Yes:
            return
        from app.services import deployment_operations_service as _dep

        try:
            _dep.get_deployment_operations_service().archive_release(rid)
        except Exception as e:
            QMessageBox.warning(self, "Deployment", str(e))
            return
        self.refresh()
