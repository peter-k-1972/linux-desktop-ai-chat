"""
Debug-Modul für Agenten-Aktivitätsüberwachung.

Bietet Event-System, Event-Bus, Debug-Store und GuiLogBuffer für transparente
Ansicht der Agenten-Aktivität.
"""

from app.debug.agent_event import AgentEvent, EventType
from app.debug.debug_store import DebugStore, get_debug_store
from app.debug.event_bus import EventBus, get_event_bus
from app.debug.gui_log_buffer import LogEntry, get_log_buffer, install_gui_log_handler

__all__ = [
    "AgentEvent",
    "EventType",
    "EventBus",
    "get_event_bus",
    "DebugStore",
    "get_debug_store",
    "LogEntry",
    "get_log_buffer",
    "install_gui_log_handler",
]
