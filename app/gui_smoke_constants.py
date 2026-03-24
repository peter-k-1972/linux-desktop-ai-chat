"""Umgebungsvariablen für GUI-Smoke-Läufe (Entrypoints + Harness)."""

from __future__ import annotations

import os
from typing import Final

# Gesetzt auf "1": GUI startet, lädt die Basis-Oberfläche, beendet sich kurz danach kontrolliert.
GUI_SMOKE_ENV: Final[str] = "LINUX_DESKTOP_CHAT_GUI_SMOKE"


def is_gui_smoke_mode() -> bool:
    return os.environ.get(GUI_SMOKE_ENV, "").strip() == "1"
