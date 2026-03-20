#!/usr/bin/env python3
"""
Startet die GUI-Shell (Standard-GUI der Anwendung).

Verwendung:
    python main.py              # Standard-Startpunkt
    python run_gui_shell.py     # Direkt
    python run_gui_shell.py --theme dark_default

Die Shell zeigt:
- Top Bar
- Navigation Sidebar (Kommandozentrale, Operations, Control Center, QA & Governance, Runtime/Debug, Settings)
- Main Workspace mit DashboardScreen und OperationsScreen (Chat-Workspace)
- Inspector Panel (rechts, kontextabhängig für Chat)
- Bottom Panel (unten)

Backend: OllamaClient, DatabaseManager, AppSettings werden initialisiert.
Theme:
- light_default (Standard)
- dark_default
"""

import argparse
import asyncio
import sys
from PySide6.QtWidgets import QApplication

from app.gui.shell import ShellMainWindow
from app.gui.themes import get_theme_manager
from app.services.infrastructure import init_infrastructure, get_infrastructure
from app.gui.chat_backend import ChatBackend, set_chat_backend
from app.gui.knowledge_backend import KnowledgeBackend, set_knowledge_backend


def main():
    import os
    from app.utils.env_loader import load_env
    from app.debug.gui_log_buffer import install_gui_log_handler
    from app.metrics.metrics_collector import get_metrics_collector
    from app.runtime.lifecycle import try_acquire_single_instance_lock, register_shutdown_hooks

    load_env()
    install_gui_log_handler()
    get_metrics_collector()

    if not try_acquire_single_instance_lock():
        print("Linux Desktop Chat läuft bereits. Nur eine Instanz ist erlaubt.")
        sys.exit(1)

    default_theme = os.environ.get("LINUX_DESKTOP_CHAT_THEME", "light_default")
    parser = argparse.ArgumentParser(description="Linux Desktop Chat – GUI Shell")
    parser.add_argument(
        "--theme",
        default=default_theme,
        choices=["light_default", "dark_default"],
        help="Theme (light_default, dark_default). Env: LINUX_DESKTOP_CHAT_THEME",
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("ollama-desktop-chat")  # StartupWMClass für Taskleisten-Gruppierung
    app.setDesktopFileName("linux-desktop-chat")   # Desktop-Integration (Wayland/GNOME)
    app.setQuitOnLastWindowClosed(True)  # Standard: Fenster schließen → App beenden
    register_shutdown_hooks(app)

    # qasync für async Chat-Integration
    try:
        from qasync import QEventLoop
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
    except ImportError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Service-Infrastruktur und Backends initialisieren
    from app.gui.qsettings_backend import create_qsettings_backend
    init_infrastructure(settings_backend=create_qsettings_backend())
    infra = get_infrastructure()
    set_chat_backend(ChatBackend())
    set_knowledge_backend(KnowledgeBackend())

    # Theme: zuerst aus persistierten Settings, sonst CLI/Env
    theme_to_apply = getattr(infra.settings, "theme_id", "") or args.theme
    if theme_to_apply not in ("light_default", "dark_default"):
        theme_to_apply = args.theme
    manager = get_theme_manager()
    if not manager.set_theme(theme_to_apply):
        print(f"Warnung: Theme '{theme_to_apply}' nicht gefunden, nutze light_default.")
        manager.set_theme("light_default")

    win = ShellMainWindow()
    win.show()

    if hasattr(loop, "run_forever"):
        with loop:
            sys.exit(loop.run_forever())
    else:
        sys.exit(app.exec())
