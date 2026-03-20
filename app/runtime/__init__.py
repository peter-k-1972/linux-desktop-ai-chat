"""
Runtime-Modul: Lifecycle, Log-Buffer.

- lifecycle: Single-Instance, Shutdown-Hooks
- gui_log_buffer: Re-Export aus app.debug (Rückwärtskompatibilität)
"""

from app.debug.gui_log_buffer import (
    LogEntry,
    get_log_buffer,
    install_gui_log_handler,
)

__all__ = [
    "LogEntry",
    "get_log_buffer",
    "install_gui_log_handler",
]
