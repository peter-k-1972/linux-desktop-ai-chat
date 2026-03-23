"""Smoke: Hilfefenster inkl. eingebetteter DocSearch."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_help_window_has_doc_search_stack(qapp):
    from app.help.help_window import HelpWindow

    win = HelpWindow(theme="light")
    assert hasattr(win, "_help_content_stack")
    assert hasattr(win, "_doc_search_panel")
    assert win._help_content_stack.count() == 2
    win._set_help_view_mode(1)
    assert win._help_content_stack.currentIndex() == 1
    win.close()
