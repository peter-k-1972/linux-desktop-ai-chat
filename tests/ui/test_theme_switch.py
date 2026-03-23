"""ThemeManager.set_theme wendet globales Stylesheet an."""

from PySide6.QtWidgets import QApplication

from app.gui.themes import get_theme_manager


def test_set_theme_updates_application_stylesheet(qapplication):
    app = QApplication.instance()
    mgr = get_theme_manager()
    assert mgr.set_theme("light_default")
    ss_light = app.styleSheet()
    assert mgr.set_theme("dark_default")
    ss_dark = app.styleSheet()
    assert ss_light != ss_dark
