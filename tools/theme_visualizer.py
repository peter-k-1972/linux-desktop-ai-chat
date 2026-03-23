#!/usr/bin/env python3
"""
Theme Visualizer — eigenständiges Dev/QA-Tool (PySide6).

Startet ohne Hauptanwendung; nutzt ThemeManager, ThemeRegistry und ThemeLoader.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from app.devtools.theme_visualizer_window import ThemeVisualizerWindow

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Theme Visualizer")
    win = ThemeVisualizerWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
