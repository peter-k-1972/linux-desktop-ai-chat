#!/usr/bin/env python3
"""
Minimal launcher for the Workbench shell (Explorer, tabbed Canvas, Inspector, Console).

Usage:
    python run_workbench_demo.py

Theme: uses the same persisted ``theme_id`` as the main shell (QSettings) when available.
"""

import sys

from PySide6.QtWidgets import QApplication

from app.gui.qsettings_backend import create_qsettings_backend
from app.gui.themes import get_theme_manager
from app.gui.themes.theme_id_utils import is_registered_theme_id
from app.gui.workbench import MainWorkbench
from app.services.infrastructure import get_infrastructure, init_infrastructure


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("ollama-desktop-chat-workbench")
    app.setQuitOnLastWindowClosed(True)

    init_infrastructure(settings_backend=create_qsettings_backend())
    theme_id = getattr(get_infrastructure().settings, "theme_id", "") or "light_default"
    manager = get_theme_manager()
    if not is_registered_theme_id(theme_id) or not manager.set_theme(theme_id):
        manager.set_theme("light_default")

    win = MainWorkbench()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
