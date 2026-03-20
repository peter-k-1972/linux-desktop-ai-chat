"""Logs Monitor – kompakte Log-Ansicht für Bottom Panel."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import QTimer
from app.debug.gui_log_buffer import get_log_buffer


class LogsMonitor(QWidget):
    """Kompakter Log-Monitor für Bottom Panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("logsMonitor")
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        title = QLabel("Logs")
        title.setStyleSheet("font-weight: 600; font-size: 12px; color: #64748b;")
        layout.addWidget(title)
        self._list = QListWidget()
        self._list.setMaximumHeight(120)
        self._list.setStyleSheet(
            "QListWidget { background: #f8fafc; border: 1px solid #e2e8f0; "
            "border-radius: 6px; font-size: 11px; }"
        )
        layout.addWidget(self._list)

    def _refresh(self) -> None:
        self._list.clear()
        try:
            entries = get_log_buffer().get_entries(limit=8)
            for e in entries:
                ts = e.timestamp.strftime("%H:%M") if e.timestamp else ""
                msg = (e.message or "")[:60]
                if len(e.message or "") > 60:
                    msg += "…"
                self._list.addItem(QListWidgetItem(f"{ts} [{e.level}] {msg}"))
            if not entries:
                self._list.addItem(QListWidgetItem("Keine Logs"))
        except Exception:
            self._list.addItem(QListWidgetItem("Log-Buffer nicht verfügbar"))
