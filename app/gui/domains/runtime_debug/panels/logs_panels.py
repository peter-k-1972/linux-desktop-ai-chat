"""
Logs Panels – Log Stream, Filter, Log Detail mit echten Daten.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QLineEdit,
    QTextEdit,
)
from PySide6.QtCore import Qt, QTimer
from app.debug.gui_log_buffer import LogEntry, get_log_buffer
from app.gui.domains.runtime_debug.rd_surface_styles import (
    rd_panel_qss,
    rd_section_title_qss,
    rd_control_qss,
    rd_monospace_table_qss,
    rd_detail_text_edit_qss,
)


class LogStreamPanel(QFrame):
    """Log Stream mit Level- und Textfilter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("logStreamPanel")
        self.setMinimumHeight(220)
        self._selected_entry: LogEntry | None = None
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(1000)

    def _setup_ui(self):
        self.setStyleSheet(rd_panel_qss())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        title = QLabel("Log Stream")
        title.setStyleSheet(rd_section_title_qss())
        header.addWidget(title)

        self._level_combo = QComboBox()
        self._level_combo.addItems(["All", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self._level_combo.setStyleSheet(rd_control_qss())
        self._level_combo.currentTextChanged.connect(self._refresh)
        header.addWidget(self._level_combo)

        self._text_filter = QLineEdit()
        self._text_filter.setPlaceholderText("Textfilter…")
        self._text_filter.setStyleSheet(rd_control_qss())
        self._text_filter.textChanged.connect(self._refresh)
        header.addWidget(self._text_filter, 1)

        header.addStretch()
        layout.addLayout(header)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Timestamp", "Level", "Module", "Message"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setStyleSheet(rd_monospace_table_qss())
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self._table)

    def _refresh(self) -> None:
        try:
            buffer = get_log_buffer()
            level = self._level_combo.currentText() or "All"
            text = self._text_filter.text().strip()
            entries = buffer.get_entries(level_filter=level if level != "All" else None, text_filter=text, limit=200)
            self._table.setRowCount(len(entries))
            for row, e in enumerate(entries):
                ts = e.timestamp.strftime("%H:%M:%S") if e.timestamp else ""
                item0 = QTableWidgetItem(ts)
                item0.setData(Qt.ItemDataRole.UserRole, e)
                self._table.setItem(row, 0, item0)
                self._table.setItem(row, 1, QTableWidgetItem(e.level))
                self._table.setItem(row, 2, QTableWidgetItem((e.module or "")[:30]))
                msg = (e.message or "")[:80]
                if len(e.message or "") > 80:
                    msg += "…"
                self._table.setItem(row, 3, QTableWidgetItem(msg))
            if not entries:
                self._table.setRowCount(1)
                self._table.setItem(0, 0, QTableWidgetItem("—"))
                self._table.setItem(0, 1, QTableWidgetItem("—"))
                self._table.setItem(0, 2, QTableWidgetItem("Keine Logs"))
                self._table.setItem(0, 3, QTableWidgetItem(""))
        except Exception:
            self._table.setRowCount(1)
            self._table.setItem(0, 0, QTableWidgetItem("—"))
            self._table.setItem(0, 1, QTableWidgetItem("—"))
            self._table.setItem(0, 2, QTableWidgetItem("Log-Buffer nicht verfügbar"))
            self._table.setItem(0, 3, QTableWidgetItem(""))

    def _on_selection_changed(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            self._selected_entry = None
        else:
            item = self._table.item(row, 0)
            self._selected_entry = item.data(Qt.ItemDataRole.UserRole) if item else None
        if hasattr(self.parent(), "on_log_selected"):
            self.parent().on_log_selected(self._selected_entry)


class LogDetailPanel(QFrame):
    """Detailansicht eines ausgewählten Log-Eintrags."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("logDetailPanel")
        self.setMinimumHeight(80)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(rd_panel_qss())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        title = QLabel("Log Detail")
        title.setStyleSheet(rd_section_title_qss())
        layout.addWidget(title)
        self._content = QTextEdit()
        self._content.setReadOnly(True)
        self._content.setStyleSheet(rd_detail_text_edit_qss())
        layout.addWidget(self._content)

    def set_entry(self, entry: LogEntry | None) -> None:
        if not entry:
            self._content.setPlaceholderText("Log-Eintrag auswählen…")
            self._content.clear()
            return
        ts = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") if entry.timestamp else ""
        lines = [f"{ts} [{entry.level}] {entry.module}", "", entry.message or ""]
        if entry.exc_text:
            lines.extend(["", "--- Exception ---", entry.exc_text])
        self._content.setPlainText("\n".join(lines))
