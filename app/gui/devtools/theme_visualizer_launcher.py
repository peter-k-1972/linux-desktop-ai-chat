"""
Single-Instance-Launcher für den Theme-Visualizer innerhalb der GUI-Shell.

Öffnet ein Top-Level-Fenster im eingebetteten Modus (kein globales Theme-Switching).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

_instance: QWidget | None = None


def reset_theme_visualizer_for_tests() -> None:
    """Nur für Tests: Referenz löschen (Fenster ggf. separat schließen)."""
    global _instance
    _instance = None


def _on_window_destroyed(*_args) -> None:
    global _instance
    _instance = None


def open_theme_visualizer(parent: QWidget | None = None) -> None:
    """
    Öffnet oder fokussiert den Theme-Visualizer.

    No-op wenn :func:`is_theme_visualizer_available` False liefert.
    """
    from app.gui.devtools.devtools_visibility import is_theme_visualizer_available

    if not is_theme_visualizer_available():
        return

    global _instance
    from app.devtools.theme_visualizer_window import ThemeVisualizerWindow

    if _instance is None:
        win = ThemeVisualizerWindow(parent=parent, embed_in_app=True)
        win.setWindowFlag(Qt.WindowType.Window, True)
        win.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        win.destroyed.connect(_on_window_destroyed)
        _instance = win
    assert _instance is not None
    _instance.show()
    _instance.raise_()
    _instance.activateWindow()
