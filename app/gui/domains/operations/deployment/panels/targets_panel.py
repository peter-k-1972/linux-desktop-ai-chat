"""R4: Deployment-Ziele — Liste, letzter Rollout, Neu/Bearbeiten.

Slice 1–2: Mit ``deployment_targets_port``: Laden + Mutationen über Presenter → Port → Adapter.
Legacy: ``deployment_targets_port=None`` — direkter Service wie zuvor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.gui.domains.operations.deployment.deployment_project_combo_data import list_project_label_id_pairs
from app.gui.domains.operations.deployment.deployment_targets_sink import DeploymentTargetsSink
from app.gui.domains.operations.deployment.dialogs.target_edit_dialog import TargetEditDialog
from app.ui_application.presenters.deployment_targets_presenter import DeploymentTargetsPresenter
from app.ui_contracts.workspaces.deployment_targets import (
    CreateDeploymentTargetCommand,
    DeploymentTargetCreateWrite,
    DeploymentTargetUpdateWrite,
    LoadDeploymentTargetsCommand,
    UpdateDeploymentTargetCommand,
)

if TYPE_CHECKING:
    from app.ui_application.ports.deployment_targets_port import DeploymentTargetsPort


class TargetsPanel(QWidget):
    def __init__(self, parent=None, *, deployment_targets_port: DeploymentTargetsPort | None = None):
        super().__init__(parent)
        self._deployment_targets_port = deployment_targets_port
        self._targets_sink: DeploymentTargetsSink | None = None
        self._targets_presenter: DeploymentTargetsPresenter | None = None

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(
            ["Name", "Art", "Projekt-ID", "Letzter Rollout", "Ergebnis"]
        )
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self._feedback = QLabel("")
        self._feedback.setObjectName("deploymentTargetsFeedback")
        self._feedback.setWordWrap(True)
        self._feedback.hide()

        new_b = QPushButton("Neu…")
        new_b.clicked.connect(self._on_new)
        edit_b = QPushButton("Bearbeiten…")
        edit_b.clicked.connect(self._on_edit)
        ref_b = QPushButton("Aktualisieren")
        ref_b.clicked.connect(self.refresh)

        bar = QHBoxLayout()
        bar.addWidget(new_b)
        bar.addWidget(edit_b)
        bar.addStretch(1)
        bar.addWidget(ref_b)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(bar)
        root.addWidget(self._feedback)
        root.addWidget(self._table, 1)

        if deployment_targets_port is not None:
            self._targets_sink = DeploymentTargetsSink(self._table, self._feedback)
            self._targets_presenter = DeploymentTargetsPresenter(
                self._targets_sink,
                deployment_targets_port,
            )

    def _use_port_path(self) -> bool:
        return self._targets_presenter is not None

    def refresh(self) -> None:
        if self._use_port_path():
            assert self._targets_presenter is not None
            self._targets_presenter.handle_command(LoadDeploymentTargetsCommand())
            return
        self._refresh_legacy()

    def _refresh_legacy(self) -> None:
        from app.services import deployment_operations_service as _dep

        svc = _dep.get_deployment_operations_service()
        last_by_t = svc.get_last_rollout_per_target()
        targets = svc.list_targets()
        self._table.setRowCount(0)
        for t in targets:
            row = self._table.rowCount()
            self._table.insertRow(row)
            lr = last_by_t.get(t.target_id)
            lr_txt = lr.recorded_at if lr else "—"
            oc_txt = lr.outcome if lr else "—"
            self._table.setItem(row, 0, QTableWidgetItem(t.name))
            self._table.setItem(row, 1, QTableWidgetItem(t.kind or ""))
            self._table.setItem(
                row, 2, QTableWidgetItem("" if t.project_id is None else str(t.project_id))
            )
            self._table.setItem(row, 3, QTableWidgetItem(lr_txt))
            self._table.setItem(row, 4, QTableWidgetItem(oc_txt))
            self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, t.target_id)

    @staticmethod
    def _deployment_project_rows() -> list[tuple[str, int]]:
        return list_project_label_id_pairs()

    def _selected_id(self) -> str | None:
        r = self._table.currentRow()
        if r < 0:
            return None
        it = self._table.item(r, 0)
        if not it:
            return None
        return it.data(Qt.ItemDataRole.UserRole)

    def _on_new(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        d = TargetEditDialog(self, title="Ziel anlegen", project_rows=self._deployment_project_rows())
        if d.exec() != d.DialogCode.Accepted:
            return
        name, kind, notes, pid = d.values()
        if self._use_port_path():
            assert self._targets_presenter is not None
            self._targets_presenter.handle_command(
                CreateDeploymentTargetCommand(
                    DeploymentTargetCreateWrite(
                        name=name,
                        kind=kind or None,
                        notes=notes or None,
                        project_id=pid,
                    ),
                ),
            )
            return
        self._on_new_legacy(name, kind, notes, pid)

    def _on_new_legacy(
        self,
        name: str,
        kind: str,
        notes: str,
        pid: int | None,
    ) -> None:
        from PySide6.QtWidgets import QMessageBox

        from app.services import deployment_operations_service as _dep

        try:
            _dep.get_deployment_operations_service().create_target(
                name=name, kind=kind or None, notes=notes or None, project_id=pid
            )
        except Exception as e:
            QMessageBox.warning(self, "Deployment", str(e))
            return
        self.refresh()

    def _on_edit(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        tid = self._selected_id()
        if not tid:
            QMessageBox.information(self, "Deployment", "Bitte ein Ziel wählen.")
            return
        if self._use_port_path():
            assert self._targets_presenter is not None
            snap = self._targets_presenter.load_snapshot_for_editor(tid)
            if snap is None:
                QMessageBox.warning(self, "Deployment", "Ziel nicht gefunden.")
                return
            d = TargetEditDialog(
                self,
                title="Ziel bearbeiten",
                initial=snap,
                project_rows=self._deployment_project_rows(),
            )
            if d.exec() != d.DialogCode.Accepted:
                return
            name, kind, notes, pid = d.values()
            self._targets_presenter.handle_command(
                UpdateDeploymentTargetCommand(
                    DeploymentTargetUpdateWrite(
                        target_id=tid,
                        name=name,
                        kind=kind or None,
                        notes=notes or None,
                        project_id=pid,
                    ),
                ),
            )
            return
        self._on_edit_legacy(tid)

    def _on_edit_legacy(self, tid: str) -> None:
        from PySide6.QtWidgets import QMessageBox

        from app.services import deployment_operations_service as _dep

        svc = _dep.get_deployment_operations_service()
        t = svc.get_target(tid)
        if not t:
            QMessageBox.warning(self, "Deployment", "Ziel nicht gefunden.")
            return
        d = TargetEditDialog(
            self,
            title="Ziel bearbeiten",
            initial=t,
            project_rows=self._deployment_project_rows(),
        )
        if d.exec() != d.DialogCode.Accepted:
            return
        name, kind, notes, pid = d.values()
        try:
            svc.update_target(
                target_id=tid,
                name=name,
                kind=kind or None,
                notes=notes or None,
                project_id=pid,
            )
        except Exception as e:
            QMessageBox.warning(self, "Deployment", str(e))
            return
        self.refresh()
