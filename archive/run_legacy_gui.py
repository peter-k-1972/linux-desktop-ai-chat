#!/usr/bin/env python3
"""
LEGACY / ARCHIVIERT – nicht der primäre Produktpfad.

Alte Chat-Oberfläche (MainWindow aus app.main) mit ChatWidget, SidebarWidget usw.

Die kanonische Anwendung startet mit: ``python -m app`` oder ``python main.py``
(→ run_gui_shell). Dieses Skript dient nur noch Wartung/Vergleich.

Aufruf vom Repository-Root: ``python archive/run_legacy_gui.py``
"""

import asyncio
from app.main import main as legacy_main

if __name__ == "__main__":
    asyncio.run(legacy_main())
