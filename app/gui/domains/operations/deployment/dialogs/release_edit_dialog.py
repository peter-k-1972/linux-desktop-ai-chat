"""Dialog: Deployment-Release anlegen/bearbeiten."""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from app.core.deployment.models import ReleaseLifecycle


class ReleaseEditDialog(QDialog):
    def __init__(
        self,
        parent=None,
        *,
        title: str = "Release",
        initial=None,
        allow_lifecycle: bool = True,
        project_rows: list[tuple[str, int]] | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self._display = QLineEdit()
        self._version = QLineEdit()
        self._artifact_kind = QLineEdit()
        self._artifact_ref = QLineEdit()
        self._lifecycle = QComboBox()
        for lab, val in (
            ("Entwurf", ReleaseLifecycle.DRAFT),
            ("Bereit", ReleaseLifecycle.READY),
            ("Archiviert", ReleaseLifecycle.ARCHIVED),
        ):
            self._lifecycle.addItem(lab, val)
        self._lifecycle.setEnabled(allow_lifecycle and initial is not None)
        self._project = QComboBox()
        self._project.addItem("(keines)", None)

        pid = None
        if initial:
            self._display.setText(initial.display_name or "")
            self._version.setText(initial.version_label or "")
            self._artifact_kind.setText(initial.artifact_kind or "")
            self._artifact_ref.setText(initial.artifact_ref or "")
            pid = initial.project_id
            for i in range(self._lifecycle.count()):
                if self._lifecycle.itemData(i) == initial.lifecycle_status:
                    self._lifecycle.setCurrentIndex(i)
                    break
        else:
            self._lifecycle.setCurrentIndex(0)

        if project_rows is not None:
            self._apply_project_rows(project_rows, select_id=pid)
        else:
            self._load_projects_legacy(select_id=pid)

        form = QFormLayout()
        form.addRow("Anzeigename:", self._display)
        form.addRow("Version:", self._version)
        form.addRow("Artefakt-Art:", self._artifact_kind)
        form.addRow("Referenz (Pfad/URI):", self._artifact_ref)
        if initial is not None:
            form.addRow("Lifecycle:", self._lifecycle)
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

    def values(self) -> tuple[str, str, str, str, Optional[str], Optional[int]]:
        lc = self._lifecycle.currentData() if self._lifecycle.isEnabled() else None
        pid = self._project.currentData()
        return (
            self._display.text().strip(),
            self._version.text().strip(),
            self._artifact_kind.text().strip(),
            self._artifact_ref.text().strip(),
            lc,
            pid,
        )
