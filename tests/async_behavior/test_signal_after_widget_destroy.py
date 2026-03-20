"""
Async Test: Spätes Signal nach Widget-Zerstörung.

Verhindert: use-after-destroy Crash wenn ein Qt-Signal nach der
Zerstörung eines Widgets eintrifft (z.B. Stream-Update nach Fensterschließen).
"""

import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SignalEmitter(QObject):
    """Eigenes Signal-Objekt, überlebt das Widget."""
    text_ready = Signal(str, bool)


class WidgetWithSlot(QWidget):
    """Widget mit Slot, der bei spätem Signal auf zerstörte Teile zugreifen könnte."""

    def __init__(self):
        super().__init__()
        self.label = QLabel("initial")
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self._received = []

    def on_update(self, text: str, is_final: bool):
        """Slot – muss defensiv sein wenn Widget bereits zerstört wird."""
        if not self.label:  # Guard: könnte None sein bei Teildestruktion
            return
        try:
            self.label.setText(text)
            self._received.append((text, is_final))
        except RuntimeError:
            # Widget bereits zerstört
            pass


@pytest.mark.async_behavior
@pytest.mark.ui
def test_signal_after_widget_destroy_no_crash(qtbot):
    """
    Signal nach Widget-Zerstörung führt zu keinem Crash.
    Szenario: Widget erzeugen → Signal verbinden → Widget löschen → Signal auslösen.
    """
    emitter = SignalEmitter()
    widget = WidgetWithSlot()
    qtbot.addWidget(widget)
    emitter.text_ready.connect(widget.on_update)

    # Widget zerstören (simuliert Fensterschließen)
    widget.deleteLater()
    qtbot.waitExposed(widget, timeout=500)
    # Event-Loop muss deleteLater verarbeiten
    qtbot.wait(100)

    # Signal auslösen – Empfänger ist zerstört
    # Qt trennt Verbindung automatisch bei Zerstörung; falls nicht: Slot muss Guards haben
    emitter.text_ready.emit("Late update", True)

    # Kein Crash, keine Exception
    qtbot.wait(50)


@pytest.mark.async_behavior
@pytest.mark.ui
def test_signal_before_destroy_delivered(qtbot):
    """
    Signal vor Zerstörung wird korrekt zugestellt.
    Kontrolltest: Verhalten bei intaktem Widget.
    """
    emitter = SignalEmitter()
    widget = WidgetWithSlot()
    qtbot.addWidget(widget)
    emitter.text_ready.connect(widget.on_update)

    emitter.text_ready.emit("Hello", True)
    qtbot.wait(50)

    assert len(widget._received) == 1
    assert widget._received[0][0] == "Hello"
    assert widget.label.text() == "Hello"
