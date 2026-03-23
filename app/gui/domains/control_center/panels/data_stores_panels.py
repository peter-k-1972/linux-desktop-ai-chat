"""
Data Stores Panels – SQLite, RAG/Chroma, Dateisystem (Messwerte, keine Demo-Zellen).
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
from app.services.infrastructure_snapshot import (
    build_data_store_rows,
    build_data_store_health_summary,
)


def _cc_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class DataStoreOverviewPanel(QFrame):
    """Übersicht: Chat-DB, RAG-Pfad, Chroma-Status aus echten Proben."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dataStoreOverviewPanel")
        self.setMinimumHeight(180)
        self._table: QTableWidget | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Data Stores")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        info = QLabel(
            "Live-Prüfung: SQLite-Datei (read-only SELECT), RAG-Basispfad und Chroma-Index-Dateien. "
            "Keine simulierten „Connected“-Zustände."
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
        self._table.setHorizontalHeaderLabels(["Store", "Typ", "Ort / Verbindung", "Zustand"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setStyleSheet(
            "QTableWidget { background: #fafafa; border: none; gridline-color: #e2e8f0; }"
        )
        layout.addWidget(self._table)
        self.refresh()

    def refresh(self) -> None:
        if not self._table:
            return
        rows = build_data_store_rows()
        self._table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self._table.setItem(i, 0, QTableWidgetItem(r.store))
            self._table.setItem(i, 1, QTableWidgetItem(r.store_type))
            self._table.setItem(i, 2, QTableWidgetItem(r.connection))
            self._table.setItem(i, 3, QTableWidgetItem(r.state))


class DataStoreHealthPanel(QFrame):
    """Kurzstatus pro Store (Farbcodes wie zuvor, Inhalt aus Snapshot)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dataStoreHealthPanel")
        self.setMinimumHeight(100)
        self._row_layout: QHBoxLayout | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Kurzstatus")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        btn_row = QHBoxLayout()
        refresh = QPushButton("Aktualisieren")
        refresh.clicked.connect(self.refresh)
        btn_row.addWidget(refresh)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._row_layout = QHBoxLayout()
        layout.addLayout(self._row_layout)
        self.refresh()

    def refresh(self) -> None:
        if not self._row_layout:
            return
        while self._row_layout.count():
            item = self._row_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for label, value, color in build_data_store_health_summary(build_data_store_rows()):
            box = QFrame()
            box.setStyleSheet("background: #f8fafc; border-radius: 6px; padding: 8px;")
            bl = QVBoxLayout(box)
            bl.setContentsMargins(12, 8, 12, 8)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #334155; font-size: 12px; font-weight: 500;")
            val = QLabel(value)
            val.setStyleSheet(f"color: {color}; font-size: 12px;")
            bl.addWidget(lbl)
            bl.addWidget(val)
            self._row_layout.addWidget(box)
