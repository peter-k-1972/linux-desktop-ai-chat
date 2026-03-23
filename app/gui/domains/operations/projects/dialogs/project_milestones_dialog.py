"""Dialog: Meilensteine eines Projekts pflegen (Phase B)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from app.projects.milestones import milestone_status_combo_entries, milestone_status_label_de


class MilestoneEditDialog(QDialog):
    """Einzelnen Meilenstein anlegen oder bearbeiten."""

    def __init__(self, project_id: int, milestone: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self._project_id = project_id
        self._milestone_id = milestone.get("milestone_id") if milestone else None
        self._sort_order = int(milestone.get("sort_order") or 0) if milestone else 0
        self.setWindowTitle("Meilenstein bearbeiten" if milestone else "Meilenstein anlegen")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)

        self._name = QLineEdit()
        layout.addRow("Name:", self._name)

        self._target = QLineEdit()
        self._target.setPlaceholderText("YYYY-MM-DD")
        layout.addRow("Zieldatum:", self._target)

        self._status = QComboBox()
        for label, val in milestone_status_combo_entries():
            self._status.addItem(label, val)
        layout.addRow("Status:", self._status)

        self._notes = QTextEdit()
        self._notes.setMaximumHeight(72)
        self._notes.setPlaceholderText("Optional")
        layout.addRow("Notiz:", self._notes)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if milestone:
            self._name.setText((milestone.get("name") or "").strip())
            self._target.setText((milestone.get("target_date") or "").strip())
            st = (milestone.get("status") or "open").strip().lower()
            for i in range(self._status.count()):
                if self._status.itemData(i) == st:
                    self._status.setCurrentIndex(i)
                    break
            else:
                self._status.insertItem(0, milestone_status_label_de(st), st)
                self._status.setCurrentIndex(0)
            self._notes.setPlainText((milestone.get("notes") or "").strip())

    def _next_sort_order(self) -> int:
        from app.services.project_service import get_project_service

        ms = get_project_service().list_project_milestones(self._project_id)
        if not ms:
            return 0
        return max(int(m.get("sort_order") or 0) for m in ms) + 1

    def accept(self) -> None:
        from app.services.project_service import get_project_service

        svc = get_project_service()
        name = (self._name.text() or "").strip()
        td = (self._target.text() or "").strip()
        st = self._status.currentData()
        notes = (self._notes.toPlainText() or "").strip()
        try:
            if self._milestone_id is None:
                so = self._next_sort_order()
                svc.create_project_milestone(
                    self._project_id,
                    name,
                    td,
                    status=str(st) if st is not None else "open",
                    sort_order=so,
                    notes=notes or None,
                )
            else:
                svc.update_project_milestone(
                    int(self._milestone_id),
                    project_id=self._project_id,
                    name=name,
                    target_date=td,
                    status=str(st) if st is not None else "open",
                    sort_order=self._sort_order,
                    notes=notes or None,
                )
        except ValueError as e:
            QMessageBox.warning(self, "Eingabe", str(e))
            return
        super().accept()


class ProjectMilestonesDialog(QDialog):
    """Liste der Meilensteine mit einfacher Reihenfolge."""

    def __init__(self, project: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._project = dict(project)
        self._pid = int(self._project["project_id"])
        self.setWindowTitle(f"Meilensteine – {self._project.get('name', 'Projekt')}")
        self.setMinimumSize(480, 360)
        root = QVBoxLayout(self)

        hint = QLabel(
            "Offene Meilensteine fließen in die Controlling-Zusammenfassung ein. "
            "Zieldatum im Format YYYY-MM-DD."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #64748b; font-size: 11px;")
        root.addWidget(hint)

        self._list = QListWidget()
        self._list.setAlternatingRowColors(True)
        root.addWidget(self._list, 1)

        row = QHBoxLayout()
        self._btn_new = QPushButton("Neu")
        self._btn_new.clicked.connect(self._on_new)
        row.addWidget(self._btn_new)
        self._btn_edit = QPushButton("Bearbeiten")
        self._btn_edit.clicked.connect(self._on_edit)
        row.addWidget(self._btn_edit)
        self._btn_del = QPushButton("Löschen")
        self._btn_del.clicked.connect(self._on_delete)
        row.addWidget(self._btn_del)
        self._btn_up = QPushButton("Nach oben")
        self._btn_up.clicked.connect(self._on_up)
        row.addWidget(self._btn_up)
        self._btn_down = QPushButton("Nach unten")
        self._btn_down.clicked.connect(self._on_down)
        row.addWidget(self._btn_down)
        row.addStretch()
        root.addLayout(row)

        btn_close = QPushButton("Schließen")
        btn_close.clicked.connect(self.accept)
        root.addWidget(btn_close)

        self._reload_list()

    def _ordered_ids(self) -> List[int]:
        out: List[int] = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            mid = item.data(Qt.ItemDataRole.UserRole)
            if mid is not None:
                out.append(int(mid))
        return out

    def _reload_list(self) -> None:
        from app.services.project_service import get_project_service

        self._list.clear()
        for m in get_project_service().list_project_milestones(self._pid):
            mid = int(m["milestone_id"])
            label = f"{m.get('target_date', '')} · {m.get('name', '')} · {milestone_status_label_de(m.get('status'))}"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, mid)
            self._list.addItem(item)

    def _on_new(self) -> None:
        dlg = MilestoneEditDialog(self._pid, None, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._reload_list()

    def _on_edit(self) -> None:
        item = self._list.currentItem()
        if not item:
            return
        mid = int(item.data(Qt.ItemDataRole.UserRole))
        from app.services.project_service import get_project_service

        row = get_project_service().get_project_milestone(mid)
        if not row:
            return
        dlg = MilestoneEditDialog(self._pid, row, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._reload_list()

    def _on_delete(self) -> None:
        item = self._list.currentItem()
        if not item:
            return
        mid = int(item.data(Qt.ItemDataRole.UserRole))
        if QMessageBox.question(self, "Löschen", "Meilenstein wirklich löschen?") != QMessageBox.StandardButton.Yes:
            return
        from app.services.project_service import get_project_service

        try:
            get_project_service().delete_project_milestone(mid, project_id=self._pid)
        except ValueError as e:
            QMessageBox.warning(self, "Fehler", str(e))
            return
        self._reload_list()

    def _on_up(self) -> None:
        r = self._list.currentRow()
        if r <= 0:
            return
        ids = self._ordered_ids()
        ids[r], ids[r - 1] = ids[r - 1], ids[r]
        self._apply_order(ids)
        self._list.setCurrentRow(r - 1)

    def _on_down(self) -> None:
        r = self._list.currentRow()
        if r < 0 or r >= self._list.count() - 1:
            return
        ids = self._ordered_ids()
        ids[r], ids[r + 1] = ids[r + 1], ids[r]
        self._apply_order(ids)
        self._list.setCurrentRow(r + 1)

    def _apply_order(self, ids: List[int]) -> None:
        from app.services.project_service import get_project_service

        try:
            get_project_service().set_project_milestones_sort_order(self._pid, ids)
        except ValueError as e:
            QMessageBox.warning(self, "Reihenfolge", str(e))
        self._reload_list()
