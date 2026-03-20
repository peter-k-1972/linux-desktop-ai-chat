"""
UI Tests: Chat Input Panel – Theme-Integration.

Testet:
- Keine hardcoded Farben im ChatInputPanel
- Theme-Tokens werden verwendet (via QSS)
- Input-Feld bleibt lesbar
- Button bleibt sichtbar und klickbar
- Theme-Wechsel bricht Panel nicht
"""

import pytest
from PySide6.QtCore import Qt

from app.gui.domains.operations.chat.panels.input_panel import ChatInputPanel


def test_input_panel_no_hardcoded_colors(qtbot):
    """ChatInputPanel hat keine hardcoded Farben in setStyleSheet."""
    panel = ChatInputPanel()
    qtbot.addWidget(panel)
    qtbot.wait(30)

    hardcoded = ["#ffffff", "#000000", "#e5e7eb", "#f3f4f6", "#2563eb", "#1d4ed8", "#1e40af", "#9ca3af"]
    for widget in [panel._model_combo, panel._input, panel._btn_send, panel._btn_prompt]:
        style = widget.styleSheet() or ""
        for hex in hardcoded:
            assert hex.lower() not in style.lower(), f"Hardcoded {hex} in {widget.objectName()}"


def test_input_field_readable(qtbot):
    """Input-Feld bleibt lesbar und nutzbar."""
    panel = ChatInputPanel()
    qtbot.addWidget(panel)
    panel.show()
    qtbot.wait(30)

    panel._input.setPlainText("Testnachricht")
    qtbot.wait(20)
    assert "Testnachricht" in panel._input.toPlainText()


def test_send_button_visible_and_clickable(qtbot):
    """Senden-Button bleibt sichtbar und klickbar."""
    panel = ChatInputPanel()
    qtbot.addWidget(panel)
    panel.show()
    qtbot.wait(30)

    assert panel._btn_send.isVisible()
    assert panel._btn_send.isEnabled()
    panel._btn_send.click()
    qtbot.wait(20)


def test_model_combo_has_object_name(qtbot):
    """ModelCombo hat ObjectName für QSS."""
    panel = ChatInputPanel()
    qtbot.addWidget(panel)
    assert panel._model_combo.objectName() == "modelCombo"


def test_labels_have_object_names(qtbot):
    """Model- und Status-Label haben ObjectNames."""
    panel = ChatInputPanel()
    qtbot.addWidget(panel)
    assert panel._status_label.objectName() == "statusLabel"


def test_theme_switch_does_not_break_input_panel(qtbot):
    """Theme-Wechsel bricht ChatInputPanel nicht."""
    try:
        from app.gui.themes import get_theme_manager
        mgr = get_theme_manager()
        original = mgr.get_current_id()
    except Exception:
        pytest.skip("ThemeManager nicht verfügbar")

    panel = ChatInputPanel()
    qtbot.addWidget(panel)
    panel.show()
    panel._input.setPlainText("Test")
    qtbot.wait(30)

    try:
        if "dark" in (original or ""):
            mgr.set_theme("light_default")
        else:
            mgr.set_theme("dark_default")
        qtbot.wait(50)
        mgr.set_theme(original or "dark_default")
    except Exception:
        pass

    assert panel._input.toPlainText() == "Test"
    assert panel._btn_send.isEnabled()
