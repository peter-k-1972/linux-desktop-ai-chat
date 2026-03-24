"""Dialog: Deployment-Ziel anlegen/bearbeiten."""

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

from app.ui_contracts.workspaces.deployment_targets import DeploymentTargetEditorSnapshotDto


class TargetEditDialog(QDialog):
    def __init__(
        self,
        parent=None,
        *,
        title: str = "Ziel",
        initial: DeploymentTargetEditorSnapshotDto | object | None = None,
        project_rows: list[tuple[str, int]] | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self._name = QLineEdit()
        self._kind = QLineEdit()
        self._notes = QTextEdit()
        self._notes.setMaximumHeight(72)
        self._project = QComboBox()
        self._project.addItem("(keines)", None)

        if initial:
            self._name.setText(initial.name or "")
            self._kind.setText(initial.kind or "")
            self._notes.setPlainText(initial.notes or "")
            pid = initial.project_id
        else:
            pid = None

        if project_rows is not None:
            self._apply_project_rows(project_rows, select_id=pid)
        else:
            self._load_projects_legacy(select_id=pid)

        form = QFormLayout()
        form.addRow("Name:", self._name)
        form.addRow("Art (optional):", self._kind)
        form.addRow("Notizen:", self._notes)
        form.addRow("Projekt:", self._project)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(buttons)

    def _apply_project_rows(self, rows: list[tuple[str, int]], *, select_id: Optional[int]) -> None:
        for label, pid in rows:
            self._project.addItem(label, int(pid))
        if select_id is not None:
            for i in range(self._project.count()):
                if self._project.itemData(i) == select_id:
                    self._project.setCurrentIndex(i)
                    break

    def _load_projects_legacy(self, *, select_id: Optional[int]) -> None:
        try:
            from app.services.project_service import get_project_service

            for p in get_project_service().list_projects():
                pid = p.get("project_id")
                if pid is None:
                    continue
                label = (p.get("name") or "").strip() or f"Projekt {pid}"
                self._project.addItem(label, int(pid))
        except Exception:
            pass
        if select_id is not None:
            for i in range(self._project.count()):
                if self._project.itemData(i) == select_id:
                    self._project.setCurrentIndex(i)
                    break

    def values(self) -> tuple[str, str, str, Optional[int]]:
        name = self._name.text().strip()
        kind = self._kind.text().strip()
        notes = self._notes.toPlainText().strip()
        pid = self._project.currentData()
        return name, kind, notes, pid
