"""
Quota-Policies: tabellarische Übersicht und Bearbeitung (Backend über ModelUsageGuiService).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHeaderView,
)

from PySide6.QtCore import Qt, Signal


def _cc_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class ModelQuotaPolicyPanel(QFrame):
    """Liste aller Quota-Policies mit Editor-Dialog."""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modelQuotaPolicyPanel")
        self._rows: List[Dict[str, Any]] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        row = QHBoxLayout()
        title = QLabel("Quota-Richtlinien")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        row.addWidget(title)
        btn = QPushButton("Aktualisieren")
        btn.clicked.connect(self._reload)
        row.addWidget(btn)
        row.addStretch()
        layout.addLayout(row)

        self._table = QTableWidget()
        self._table.setColumnCount(10)
        self._table.setHorizontalHeaderLabels(
            [
                "ID",
                "Aktiv",
                "Scope",
                "Modell",
                "Provider",
                "Modus",
                "Quelle",
                "Warn %",
                "Limit (T)",
                "Notiz",
            ]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.doubleClicked.connect(self._on_edit)
        layout.addWidget(self._table)

        edit_btn = QPushButton("Ausgewählte bearbeiten…")
        edit_btn.clicked.connect(self._on_edit)
        layout.addWidget(edit_btn)

        self._hint = QLabel("")
        self._hint.setStyleSheet("color: #64748b; font-size: 11px;")
        self._hint.setWordWrap(True)
        layout.addWidget(self._hint)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._reload()

    def _reload(self) -> None:
        from app.services.model_usage_gui_service import get_model_usage_gui_service

        self._rows = get_model_usage_gui_service().list_all_policies()
        self._table.setRowCount(len(self._rows))
        for i, r in enumerate(self._rows):
            self._table.setItem(i, 0, QTableWidgetItem(str(r.get("id", ""))))
            self._table.setItem(i, 1, QTableWidgetItem("ja" if r.get("enabled") else "nein"))
            st = f"{r.get('scope_type', '')}"
            if r.get("scope_ref"):
                st += f" ({r.get('scope_ref')})"
            self._table.setItem(i, 2, QTableWidgetItem(st))
            self._table.setItem(i, 3, QTableWidgetItem(str(r.get("model_id") or "—")))
            self._table.setItem(i, 4, QTableWidgetItem(str(r.get("provider_id") or "—")))
            self._table.setItem(i, 5, QTableWidgetItem(str(r.get("mode", ""))))
            self._table.setItem(i, 6, QTableWidgetItem(str(r.get("source", ""))))
            self._table.setItem(i, 7, QTableWidgetItem(str(r.get("warn_percent", ""))))
            lt = r.get("limit_total")
            self._table.setItem(i, 8, QTableWidgetItem("" if lt is None else str(lt)))
            self._table.setItem(i, 9, QTableWidgetItem(str(r.get("notes") or "")[:40]))
        self._hint.setText(
            "Doppelklick oder Bearbeiten: Modus, Limits, Warnschwelle. "
            "Offline-Standardrichtlinien haben scope_type „offline_default“."
        )

    def _selected_row(self) -> Optional[Dict[str, Any]]:
        items = self._table.selectedItems()
        if not items:
            return None
        row = items[0].row()
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def _on_edit(self) -> None:
        r = self._selected_row()
        if not r:
            QMessageBox.information(self, "Quota", "Bitte eine Zeile auswählen.")
            return
        dlg = _PolicyEditDialog(r, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._reload()
            self.refresh_requested.emit()


class _PolicyEditDialog(QDialog):
    def __init__(self, row: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._row = row
        self.setWindowTitle(f"Quota-Policy #{row.get('id')}")
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._enabled = QCheckBox("Aktiv")
        self._enabled.setChecked(bool(row.get("enabled")))
        form.addRow(self._enabled)

        self._mode = QComboBox()
        for m in ("none", "warn", "hard_block"):
            self._mode.addItem(m, m)
        idx = self._mode.findData(row.get("mode"))
        self._mode.setCurrentIndex(max(0, idx))

        self._warn = QDoubleSpinBox()
        self._warn.setRange(0.0, 1.0)
        self._warn.setSingleStep(0.05)
        self._warn.setValue(float(row.get("warn_percent") or 0.8))
        form.addRow("Modus", self._mode)
        form.addRow("Warnschwelle (0–1)", self._warn)

        def _spin(val: Any) -> QSpinBox:
            s = QSpinBox()
            s.setRange(0, 2_000_000_000)
            s.setValue(int(val or 0))
            s.setToolTip("0 = kein Limit für dieses Fenster")
            return s

        self._lh = _spin(row.get("limit_hour"))
        self._ld = _spin(row.get("limit_day"))
        self._lw = _spin(row.get("limit_week"))
        self._lm = _spin(row.get("limit_month"))
        self._lt = _spin(row.get("limit_total"))
        form.addRow("Limit Stunde", self._lh)
        form.addRow("Limit Tag", self._ld)
        form.addRow("Limit Woche", self._lw)
        form.addRow("Limit Monat", self._lm)
        form.addRow("Limit gesamt", self._lt)

        self._notes = QLineEdit(str(row.get("notes") or ""))
        form.addRow("Notiz", self._notes)

        layout.addLayout(form)

        ro = QLabel(
            f"Scope: {row.get('scope_type')} / ref: {row.get('scope_ref') or '—'} · "
            f"Modell: {row.get('model_id') or '—'} · Quelle: {row.get('source')}"
        )
        ro.setStyleSheet("color: #64748b; font-size: 11px;")
        ro.setWordWrap(True)
        layout.addWidget(ro)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self) -> None:
        from app.services.model_usage_gui_service import get_model_usage_gui_service

        def lim(s: QSpinBox) -> Optional[int]:
            v = int(s.value())
            return None if v <= 0 else v

        res = get_model_usage_gui_service().save_policy(
            int(self._row["id"]),
            is_enabled=self._enabled.isChecked(),
            mode=str(self._mode.currentData()),
            warn_percent=float(self._warn.value()),
            limit_hour=lim(self._lh),
            limit_day=lim(self._ld),
            limit_week=lim(self._lw),
            limit_month=lim(self._lm),
            limit_total=lim(self._lt),
            notes=self._notes.text().strip() or None,
        )
        if not res.get("ok"):
            QMessageBox.warning(self, "Speichern", res.get("error") or "Fehler")
            return
        self.accept()
