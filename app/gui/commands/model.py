"""
Command – Modell für eine ausführbare Aktion.
"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class Command:
    """
    Ein Befehl für die Command Palette.

    Attributes:
        id: Eindeutige Kennung (z.B. "nav.dashboard")
        title: Anzeigename (z.B. "Open Dashboard")
        description: Optionale Beschreibung
        icon: Icon-Name für IconManager (z.B. "dashboard")
        category: Kategorie für Gruppierung (navigation, system, search)
        callback: Auszuführende Aktion (ohne Argumente)
    """

    id: str
    title: str
    description: str = ""
    icon: str = ""
    category: str = "navigation"
    callback: Callable[[], None] | None = None

    def execute(self) -> None:
        """Führt den Command aus."""
        if self.callback:
            self.callback()
