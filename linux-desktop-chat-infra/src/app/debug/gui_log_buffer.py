"""
GUI Log Buffer – speichert Log-Einträge für die Runtime/Debug-GUI.

Ein logging.Handler leitet Python-Logs in einen ring-buffered Store.
Die GUI kann get_log_buffer().get_entries() abfragen.
"""

import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

MAX_LOG_ENTRIES = 1000


@dataclass
class LogEntry:
    """Ein Log-Eintrag für die GUI."""

    timestamp: datetime
    level: str
    module: str
    message: str
    exc_text: Optional[str] = None


class LogBuffer:
    """Thread-sicherer Ring-Puffer für Log-Einträge."""

    def __init__(self, max_entries: int = MAX_LOG_ENTRIES):
        self._entries: List[LogEntry] = []
        self._max = max_entries
        self._lock = threading.RLock()

    def append(self, entry: LogEntry) -> None:
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self._max:
                self._entries = self._entries[-self._max:]

    def get_entries(
        self,
        level_filter: Optional[str] = None,
        text_filter: str = "",
        module_filter: Optional[str] = None,
        limit: int = 500,
    ) -> List[LogEntry]:
        """Liefert Einträge (neueste zuerst), optional gefiltert."""
        with self._lock:
            result = list(reversed(self._entries))
            if level_filter and level_filter != "All":
                result = [e for e in result if e.level == level_filter]
            if text_filter:
                t = text_filter.lower()
                result = [e for e in result if t in (e.message or "").lower() or t in (e.module or "").lower()]
            if module_filter and module_filter != "All":
                result = [e for e in result if (e.module or "").startswith(module_filter)]
            return result[:limit]

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


class GuiLogHandler(logging.Handler):
    """Logging-Handler, der Einträge in den LogBuffer schreibt."""

    def __init__(self, buffer: LogBuffer):
        super().__init__()
        self._buffer = buffer

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            exc_text = None
            if record.exc_info:
                exc_text = logging.Formatter().formatException(record.exc_info)
            entry = LogEntry(
                timestamp=datetime.fromtimestamp(record.created),
                level=record.levelname,
                module=record.name or "",
                message=msg,
                exc_text=exc_text,
            )
            self._buffer.append(entry)
        except Exception:
            self.handleError(record)


_buffer: Optional[LogBuffer] = None
_handler: Optional[GuiLogHandler] = None


def get_log_buffer() -> LogBuffer:
    """Liefert den globalen LogBuffer."""
    global _buffer
    if _buffer is None:
        _buffer = LogBuffer()
    return _buffer


def install_gui_log_handler() -> None:
    """Installiert den GUI-Log-Handler am Root-Logger."""
    global _handler
    if _handler is not None:
        return
    buffer = get_log_buffer()
    _handler = GuiLogHandler(buffer)
    _handler.setLevel(logging.DEBUG)
    _handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger()
    root.addHandler(_handler)
    root.setLevel(logging.DEBUG)
