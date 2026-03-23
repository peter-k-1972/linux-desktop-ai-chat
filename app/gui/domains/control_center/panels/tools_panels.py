"""
Tools Panels – eingebaute Werkzeuge und Konfigurationsstatus (keine fiktive Registry).
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
)
from app.services.infrastructure_snapshot import build_tool_snapshot_rows


def _cc_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class ToolRegistryPanel(QFrame):
    """Übersicht der im Produkt vorhandenen Tool-Pfade (Datei, Web-Suche, RAG, Commands)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolRegistryPanel")
        self.setMinimumHeight(200)
        self._table: QTableWidget | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Tools & Integration")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        info = QLabel(
            "Live-Status aus lokaler Konfiguration (keine externe Tool-Registry). "
            "Die Tabelle listet eingebaute Fähigkeiten, keine Drittanbieter-Plugins."
        )
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 11px; color: #64748b; margin-bottom: 8px;")
        layout.addWidget(info)

        btn_row = QHBoxLayout()
        refresh = QPushButton("Aktualisieren")
        refresh.clicked.connect(self.refresh)
        btn_row.addWidget(refresh)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Tool", "Kategorie", "Berechtigung / Umfang", "Status"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setStyleSheet(
            "QTableWidget { background: #fafafa; border: none; gridline-color: #e2e8f0; }"
        )
        layout.addWidget(self._table)
        self.refresh()

    def refresh(self) -> None:
        if not self._table:
            return
        rows = build_tool_snapshot_rows()
        self._table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self._table.setItem(i, 0, QTableWidgetItem(r.tool_id))
            self._table.setItem(i, 1, QTableWidgetItem(r.category))
            self._table.setItem(i, 2, QTableWidgetItem(r.permissions))
            self._table.setItem(i, 3, QTableWidgetItem(r.status))


class ToolSummaryPanel(QFrame):
    """Kurzüberblick: Anzahl sichtbarer Tool-Zeilen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolSummaryPanel")
        self.setMinimumHeight(100)
        self._summary_label: QLabel | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Zusammenfassung")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._summary_label = QLabel("")
        self._summary_label.setWordWrap(True)
        self._summary_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._summary_label)
        self.refresh()

    def refresh(self) -> None:
        if not self._summary_label:
            return
        n = len(build_tool_snapshot_rows())
        self._summary_label.setText(
            f"{n} eingebaute Tool-Zeilen · Details siehe Tabelle oben · "
            "Keine automatische Plugin-Liste."
        )
