"""
Model Usage View – zeigt verwendete Modelle, Aufrufe und Dauer.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt

from app.debug.debug_store import DebugStore, ModelUsageEntry
from app.resources.styles import get_theme_colors


class ModelUsageView(QWidget):
    """Zeigt Modellnutzung: Modell, Aufrufe, Dauer."""

    def __init__(self, store: DebugStore, theme: str = "dark", parent=None):
        super().__init__(parent)
        self._store = store
        self._theme = theme
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        title = QLabel("Modellnutzung")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Modell", "Aufrufe", "Dauer (s)"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setMinimumHeight(120)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

    def _get_styles(self) -> dict:
        return get_theme_colors(self._theme)

    def refresh(self):
        """Aktualisiert die Tabelle aus dem DebugStore."""
        colors = self._get_styles()
        fg = colors.get("fg", "#e8e8e8")

        entries = self._store.get_model_usage()
        self._table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            self._table.setItem(row, 0, QTableWidgetItem(entry.model_id))
            self._table.setItem(row, 1, QTableWidgetItem(str(entry.call_count)))
            dur = f"{entry.total_duration_sec:.1f}" if entry.total_duration_sec else "-"
            self._table.setItem(row, 2, QTableWidgetItem(dur))

    def set_theme(self, theme: str):
        """Setzt das Theme."""
        self._theme = theme
