"""
Regression: ChatComposer send_requested Signal wird nicht ausgelöst.

Bug: test_chat_composer_send_signal prüfte nur `send_requested is not None`,
was immer True ist. Der Test war grün, obwohl das Signal möglicherweise
nie ausgelöst wurde.

Erwartung: Nach Klick auf Senden (oder Return) muss das Signal tatsächlich
emittiert werden (z.B. received-Liste nicht leer).
"""

import pytest

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

from app.gui.domains.operations.chat.panels.chat_composer_widget import ChatComposerWidget, ChatInput


@pytest.mark.regression
@pytest.mark.ui
def test_chat_composer_send_signal_actually_emits(qtbot):
    """
    Signal send_requested muss nach Senden-Aktion tatsächlich emittiert werden.
    """
    composer = ChatComposerWidget(icons_path="")
    qtbot.addWidget(composer)
    received = []

    def on_send():
        received.append(True)

    composer.send_requested.connect(on_send)

    input_widget = composer.findChild(ChatInput)
    assert input_widget is not None
    qtbot.keyClicks(input_widget, "Test-Nachricht")

    # Senden-Button klicken
    for btn in composer.findChildren(QPushButton):
        if "send" in (btn.objectName() or "").lower() or "Senden" in btn.text():
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
            break
    qtbot.wait(100)

    # Signal muss tatsächlich ausgelöst worden sein
    assert len(received) >= 1, "send_requested Signal wurde nicht emittiert"
