#!/usr/bin/env python3
"""
LEGACY: Alte GUI – Chat-Oberfläche mit Backend-Integration.

Startet die frühere MainWindow mit:
- ChatWidget, SidebarWidget, CommandCenterView
- OllamaClient, ModelOrchestrator, RAGService
- Asynchrone Event-Loop (qasync)

Diese Oberfläche ist deprecated. Die neue GUI-Shell ist der Standard.
Verwendung: python run_legacy_gui.py
"""

import asyncio
from app.main import main as legacy_main

if __name__ == "__main__":
    asyncio.run(legacy_main())
