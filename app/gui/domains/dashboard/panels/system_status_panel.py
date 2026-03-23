"""
SystemStatusPanel – Ollama-Erreichbarkeit und Chat-DB-Kurzstatus.
"""

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from app.gui.shared import BasePanel
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.services.infrastructure_snapshot import probe_ollama_localhost, build_data_store_rows


class SystemStatusPanel(BasePanel):
    """Panel: lokale Laufzeit (Ollama, SQLite aus Snapshot)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self._status: QLabel | None = None
        self._detail: QLabel | None = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title_row = QWidget()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(8)
        icon_label = QLabel()
        icon_label.setPixmap(IconManager.get(IconRegistry.CONTROL, size=18).pixmap(18, 18))
        title_row_layout.addWidget(icon_label)
        title = QLabel("System Status")
        title.setObjectName("panelTitle")
        title_row_layout.addWidget(title)
        title_row_layout.addStretch()
        layout.addWidget(title_row)

        self._status = QLabel("—")
        self._status.setObjectName("panelStatus")
        layout.addWidget(self._status)

        self._detail = QLabel("")
        self._detail.setObjectName("panelMeta")
        self._detail.setWordWrap(True)
        layout.addWidget(self._detail)

        layout.addStretch()

    def refresh(self) -> None:
        if not self._status or not self._detail:
            return
        ok, hint = probe_ollama_localhost()
        rows = build_data_store_rows()
        db_state = rows[0].state if rows else "—"
        if ok:
            self._status.setText("Ollama erreichbar")
            self._status.setStyleSheet("")
        else:
            self._status.setText("Ollama nicht erreichbar")
            self._status.setStyleSheet("color: #b45309;")
        self._detail.setText(
            f"Lokal: {hint} · Chat-DB: {db_state}. "
            "RAG/Chroma siehe Control Center → Data Stores."
        )
