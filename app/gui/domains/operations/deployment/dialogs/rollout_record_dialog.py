"""Dialog: Rollout protokollieren (insert-only)."""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

from app.core.deployment.models import ReleaseLifecycle, RolloutOutcome


class RolloutRecordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rollout protokollieren")
        self._target = QComboBox()
        self._release = QComboBox()
        self._outcome = QComboBox()
        self._outcome.addItem("Erfolg", RolloutOutcome.SUCCESS)
        self._outcome.addItem("Fehlgeschlagen", RolloutOutcome.FAILED)
        self._outcome.addItem("Abgebrochen", RolloutOutcome.CANCELLED)
        self._message = QTextEdit()
        self._message.setMaximumHeight(64)
        self._started = QLineEdit()
        self._finished = QLineEdit()
        self._started.setPlaceholderText("ISO-Zeit optional")
        self._finished.setPlaceholderText("ISO-Zeit optional")
        self._run_id = QLineEdit()
        self._run_id.setPlaceholderText("optional workflow_run_id")

        self._reload_combos()

        form = QFormLayout()
        form.addRow("Ziel:", self._target)
        form.addRow("Release (nur „bereit“):", self._release)
        form.addRow("Ergebnis:", self._outcome)
        form.addRow("Nachricht:", self._message)
        form.addRow("Gestartet:", self._started)
        form.addRow("Beendet:", self._finished)
        form.addRow("Workflow-Run:", self._run_id)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(buttons)

    def _reload_combos(self) -> None:
        from app.services import deployment_operations_service as _dep

        svc = _dep.get_deployment_operations_service()
        self._target.clear()
        for t in svc.list_targets():
            self._target.addItem(t.name, t.target_id)
        self._release.clear()
        for r in svc.list_releases(lifecycle_status=ReleaseLifecycle.READY):
            label = f"{r.display_name} ({r.version_label})"
            self._release.addItem(label, r.release_id)

    def values(self) -> tuple[str, str, str, str, Optional[str], Optional[str], Optional[str]]:
        tid = self._target.currentData()
        rid = self._release.currentData()
        oc = self._outcome.currentData()
        msg = self._message.toPlainText().strip()
        return (
            tid or "",
            rid or "",
            oc or "",
            msg or "",
            self._started.text().strip() or None,
            self._finished.text().strip() or None,
            self._run_id.text().strip() or None,
        )
