"""
R3: Periodischer Tick für fällige Schedules — kein Scheduler, nur Anstoß.

``tick_due`` läuft im Thread-Pool; UI-Thread bleibt frei.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal, Slot

_log = logging.getLogger(__name__)


class _TickSignals(QObject):
    tick_done = Signal()


class _TickRunnable(QRunnable):
    def __init__(self, signals: _TickSignals) -> None:
        super().__init__()
        self._signals = signals

    def run(self) -> None:
        try:
            from app.services.schedule_service import get_schedule_service

            now = datetime.now(timezone.utc)
            n = get_schedule_service().tick_due(now)
            if n:
                _log.debug("schedule tick_due: %s Run(s) gestartet", n)
        except Exception:
            _log.exception("schedule tick_due fehlgeschlagen")
        finally:
            self._signals.tick_done.emit()


class ScheduleTickController(QObject):
    """Ein QTimer pro Fenster; parallele Ticks werden unterdrückt."""

    def __init__(self, parent=None, *, interval_ms: int = 45_000) -> None:
        super().__init__(parent)
        self._interval_ms = int(interval_ms)
        self._timer = QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._on_timer)
        self._pool = QThreadPool.globalInstance()
        self._signals = _TickSignals(self)
        self._signals.tick_done.connect(self._on_tick_done)
        self._busy = False

    def start(self) -> None:
        if self._interval_ms <= 0:
            return
        self._timer.start(self._interval_ms)
        _log.info("Schedule-Ticker gestartet (alle %s ms)", self._interval_ms)

    def stop(self) -> None:
        self._timer.stop()
        _log.info("Schedule-Ticker gestoppt")

    @Slot()
    def _on_timer(self) -> None:
        if self._busy:
            return
        self._busy = True
        self._pool.start(_TickRunnable(self._signals))

    @Slot()
    def _on_tick_done(self) -> None:
        self._busy = False
