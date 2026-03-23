"""
R2: Plattform-Gesundheit (Monitoring light) – nur Lesen + Refresh.

Health-Build läuft im Thread-Pool; UI-Thread blockiert nicht auf Probes.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.gui.shared import BasePanel
from app.qa.operations_models import HealthCheckResult, PlatformHealthSummary


class _PlatformHealthSignals(QObject):
    """Signale nur im GUI-Thread auswerten (QueuedConnection über Threads)."""

    load_done = Signal(int, object)  # token, PlatformHealthSummary | Exception


class _PlatformHealthRunnable(QRunnable):
    def __init__(self, token: int, signals: _PlatformHealthSignals) -> None:
        super().__init__()
        self._token = token
        self._signals = signals

    def run(self) -> None:
        from app.services.platform_health_service import build_platform_health_summary

        try:
            summary = build_platform_health_summary()
            self._signals.load_done.emit(self._token, summary)
        except Exception as exc:
            self._signals.load_done.emit(self._token, exc)


class PlatformHealthPanel(BasePanel):
    """Zeigt Health-Checks; kein Hintergrund-Polling."""

    def __init__(self, parent=None, thread_pool: QThreadPool | None = None):
        super().__init__(parent)
        self.setObjectName("platformHealthPanel")
        self._pool = thread_pool if thread_pool is not None else QThreadPool.globalInstance()
        # Signale an App (oder Fallback self) hängen, damit Worker nach Panel-Zerstörung nicht
        # auf ein bereits gelöschtes QObject emittiert.
        _sig_parent = QApplication.instance() or self
        self._signals = _PlatformHealthSignals(_sig_parent)
        self._signals.load_done.connect(self._on_load_done)
        self.destroyed.connect(self._disconnect_load_done)
        self._refresh_token = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        head = QHBoxLayout()
        self._overall = QLabel("—")
        self._overall.setObjectName("platformHealthOverall")
        head.addWidget(self._overall)
        head.addStretch()
        self._btn_refresh = QPushButton("Erneut prüfen")
        self._btn_refresh.clicked.connect(self.refresh)
        head.addWidget(self._btn_refresh)
        layout.addLayout(head)

        self._checked = QLabel("")
        self._checked.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._checked)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Check", "Status", "Detail"])
        self._table.setEditTriggers(self._table.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(self._table.SelectionMode.NoSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table, 1)

    def _disconnect_load_done(self, _obj: object | None = None) -> None:
        try:
            self._signals.load_done.disconnect(self._on_load_done)
        except (TypeError, RuntimeError):
            pass

    def refresh(self) -> None:
        self._refresh_token += 1
        token = self._refresh_token
        self._btn_refresh.setEnabled(False)
        self._overall.setText("Prüfung läuft…")
        self._pool.start(_PlatformHealthRunnable(token, self._signals))

    @Slot(int, object)
    def _on_load_done(self, token: int, result: object) -> None:
        if token != self._refresh_token:
            return
        self._btn_refresh.setEnabled(True)
        if isinstance(result, Exception):
            summary = PlatformHealthSummary(
                overall="error",
                checked_at="",
                checks=[
                    HealthCheckResult(
                        check_id="health:fatal",
                        severity="error",
                        title="Health-Abfrage",
                        detail=str(result),
                    )
                ],
            )
            self._apply_summary(summary)
            return
        self._apply_summary(result)

    def _apply_summary(self, summary: PlatformHealthSummary) -> None:
        ov = (summary.overall or "ok").lower()
        label = {"ok": "Gesamt: OK", "warning": "Gesamt: Warnung", "error": "Gesamt: Fehler"}.get(
            ov, f"Gesamt: {ov}"
        )
        self._overall.setText(label)
        self._checked.setText(f"Geprüft: {summary.checked_at or '—'}")
        self._table.setRowCount(0)
        for c in summary.checks:
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(c.title))
            sev_item = QTableWidgetItem(c.severity.upper())
            sev_item.setData(Qt.ItemDataRole.UserRole, c.severity)
            self._table.setItem(r, 1, sev_item)
            self._table.setItem(r, 2, QTableWidgetItem(c.detail))
        self._table.resizeColumnsToContents()
