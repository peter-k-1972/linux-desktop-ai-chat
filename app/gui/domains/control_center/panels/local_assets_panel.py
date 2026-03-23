"""
Lokale Modell-Speicherorte und Assets (Inventar, kein Dateimanager).
"""

from __future__ import annotations

from typing import Any, Dict, List

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHeaderView,
)

from PySide6.QtCore import Signal


def _cc_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class LocalModelAssetsPanel(QFrame):
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("localModelAssetsPanel")
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        row = QHBoxLayout()
        title = QLabel("Lokale Speicherorte & Assets")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        row.addWidget(title)
        btn = QPushButton("Aktualisieren")
        btn.clicked.connect(self._reload)
        row.addWidget(btn)
        scan_btn = QPushButton("Speicherorte scannen")
        scan_btn.clicked.connect(self._run_scan)
        row.addWidget(scan_btn)
        row.addStretch()
        layout.addLayout(row)

        self._roots_table = QTableWidget()
        self._roots_table.setColumnCount(6)
        self._roots_table.setHorizontalHeaderLabels(
            ["Name", "Pfad", "Aktiv", "Managed", "Nur-Lese", "Scan"]
        )
        self._roots_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("Storage Roots"))
        layout.addWidget(self._roots_table)

        self._assets_table = QTableWidget()
        self._assets_table.setColumnCount(7)
        self._assets_table.setHorizontalHeaderLabels(
            ["Modell", "Root", "Typ", "Status", "Verfügbar", "Pfad", "ID"],
        )
        self._assets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("Assets"))
        layout.addWidget(self._assets_table)

        self._hint = QLabel("")
        self._hint.setWordWrap(True)
        self._hint.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(self._hint)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._reload()

    def _run_scan(self) -> None:
        from app.services.model_usage_gui_service import get_model_usage_gui_service

        rep = get_model_usage_gui_service().run_local_inventory_scan()
        if not rep.get("ok"):
            self._hint.setText(f"Scan fehlgeschlagen: {rep.get('error', '—')}")
            return
        err_n = len(rep.get("errors") or [])
        err_part = f" Hinweise/Fehler: {err_n}." if err_n else ""
        self._hint.setText(
            f"Scan abgeschlossen: {rep.get('created', 0)} neu, {rep.get('updated', 0)} aktualisiert, "
            f"{rep.get('marked_unavailable', 0)} als fehlend, {rep.get('unassigned_count', 0)} ohne Modell, "
            f"{rep.get('skipped_roots', 0)} Root(s) übersprungen.{err_part}"
        )
        self._reload()

    def _reload(self) -> None:
        from app.services.model_usage_gui_service import get_model_usage_gui_service

        data = get_model_usage_gui_service().list_all_assets_flat()
        if data.get("db_error"):
            self._hint.setText(f"Datenbank: {data['db_error']}")
            return
        roots: List[Dict[str, Any]] = data.get("roots") or []
        assets: List[Dict[str, Any]] = data.get("assets") or []

        self._roots_table.setRowCount(len(roots))
        for i, r in enumerate(roots):
            self._roots_table.setItem(i, 0, QTableWidgetItem(str(r.get("name", ""))))
            self._roots_table.setItem(i, 1, QTableWidgetItem(str(r.get("path_absolute", ""))))
            self._roots_table.setItem(i, 2, QTableWidgetItem("ja" if r.get("is_enabled") else "nein"))
            self._roots_table.setItem(i, 3, QTableWidgetItem("ja" if r.get("is_managed") else "nein"))
            self._roots_table.setItem(i, 4, QTableWidgetItem("ja" if r.get("is_read_only") else "nein"))
            self._roots_table.setItem(i, 5, QTableWidgetItem("ja" if r.get("scan_enabled") else "nein"))

        self._assets_table.setRowCount(len(assets))
        for i, a in enumerate(assets):
            self._assets_table.setItem(i, 0, QTableWidgetItem(str(a.get("model_id") or "—")))
            self._assets_table.setItem(i, 1, QTableWidgetItem(str(a.get("storage_root_name") or "—")))
            self._assets_table.setItem(i, 2, QTableWidgetItem(str(a.get("asset_type", ""))))
            self._assets_table.setItem(i, 3, QTableWidgetItem(str(a.get("status_label", ""))))
            self._assets_table.setItem(i, 4, QTableWidgetItem("ja" if a.get("is_available") else "nein"))
            self._assets_table.setItem(i, 5, QTableWidgetItem(str(a.get("path_absolute", ""))))
            self._assets_table.setItem(i, 6, QTableWidgetItem(str(a.get("id", ""))))

        unassigned = sum(1 for a in assets if not (str(a.get("model_id") or "").strip()))
        missing = sum(1 for a in assets if not a.get("is_available"))
        self._hint.setText(
            f"{len(roots)} Root(s), {len(assets)} Asset(s). "
            f"Nicht zugewiesen: {unassigned}, als fehlend markiert: {missing}."
        )
