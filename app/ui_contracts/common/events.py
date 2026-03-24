"""
UI-seitige Ereignisse (für Telemetrie, Logging, spätere Event-Bus-Anbindung).

Keine Qt-Signale — nur transportfähige Daten.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class ChatUiEvent:
    """
    Generisches Chat-UI-Ereignis.

    ``payload`` ist absichtlich schwach typisiert, damit Contracts stabil bleiben,
    ohne alle Domänendetails vorab festzunageln.
    """

    kind: Literal[
        "chat_selected",
        "chat_created",
        "message_send_requested",
        "stream_started",
        "stream_stopped",
        "error",
    ]
    payload: dict[str, Any]
