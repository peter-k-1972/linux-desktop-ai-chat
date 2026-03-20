#!/usr/bin/env python3
"""
Setzt den Chat-Kontextmodus – ohne UI.

Verwendung:
  python scripts/dev/set_context_mode.py semantic
  python scripts/dev/set_context_mode.py neutral
  python scripts/dev/set_context_mode.py off

Lädt Settings, setzt chat_context_mode, speichert.
Ideal für QA, Tests, Experimente.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

VALID_MODES = ("off", "neutral", "semantic")


def main() -> int:
    if len(sys.argv) != 2:
        print("Verwendung: python set_context_mode.py <semantic|neutral|off>")
        return 1

    raw = sys.argv[1].strip().lower()
    if raw not in VALID_MODES:
        print(f"Fehler: Ungültiger Modus '{raw}'. Erlaubt: off, neutral, semantic")
        return 1

    from app.core.config.settings import AppSettings
    from app.gui.qsettings_backend import create_qsettings_backend

    backend = create_qsettings_backend()
    settings = AppSettings(backend=backend)
    settings.chat_context_mode = raw
    settings.save()

    print(f"ChatContextMode: {raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
