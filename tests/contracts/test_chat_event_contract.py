"""
Contract Tests: Chat update_chat_signal Event-Vertrag.

Sichert den Vertrag zwischen ChatWidget.update_chat_signal und allen Konsumenten
(ConversationView, _on_update_chat_slot, Debug/Timeline).
Verhindert: Event-Struktur-Drift, falsche Payload-Typen → ui_state_drift.

event_contract_guard für Subsystem Chat (GG-001, RTB-001).
"""

import pytest

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings


class MinimalChatWidgetForContract(ChatWidget):
    """ChatWidget ohne Modell-Load für Contract-Tests."""

    def load_models(self):
        pass


class FakeDB:
    def __init__(self):
        self._messages = {}
        self._next_id = 1

    def create_chat(self, title=""):
        cid = self._next_id
        self._next_id += 1
        self._messages[cid] = []
        return cid

    def save_message(self, cid, role, content):
        self._messages.setdefault(cid, []).append((role, content, "ts"))

    def load_chat(self, cid):
        return list(self._messages.get(cid, []))

    def list_workspace_roots_for_chat(self, cid):
        return []


@pytest.fixture
def chat_widget_for_contract(qtbot):
    """Minimales ChatWidget für Signal-Contract-Tests."""
    from unittest.mock import MagicMock, AsyncMock
    client = MagicMock()
    client.get_models = AsyncMock(return_value=[])
    settings = AppSettings()
    settings.model = "test:latest"
    settings.theme = "dark"
    settings.icons_path = ""
    settings.save = lambda: None
    settings.think_mode = "auto"
    settings.rag_enabled = False
    settings.auto_routing = True
    settings.cloud_escalation = False
    settings.overkill_mode = False
    settings.web_search = False
    db = FakeDB()
    widget = MinimalChatWidgetForContract(client, settings, db)
    qtbot.addWidget(widget)
    return widget


# Vertrag: update_chat_signal = Signal(str, bool)  # (text, is_final)
# Pflichtfelder: text: str, is_final: bool
# Drift bei Änderung → UI zeigt falschen Zustand (ui_state_drift)


@pytest.mark.contract
@pytest.mark.ui
def test_chat_update_signal_emits_str_bool(chat_widget_for_contract):
    """
    update_chat_signal emittiert (text: str, is_final: bool).
    Vertrag: Konsumenten erwarten genau diese Signatur.
    Drift: zusätzliche Parameter oder falsche Typen → ui_state_drift.
    """
    received = []

    def capture(text, is_final):
        received.append((text, is_final))

    chat_widget_for_contract.update_chat_signal.connect(capture)
    chat_widget_for_contract._safe_emit_update("Hallo", True)

    assert len(received) == 1
    text, is_final = received[0]
    assert isinstance(text, str), "text muss str sein"
    assert isinstance(is_final, bool), "is_final muss bool sein"
    assert text == "Hallo"
    assert is_final is True


@pytest.mark.contract
@pytest.mark.ui
def test_chat_update_signal_payload_form_stable(chat_widget_for_contract):
    """
    Payload-Form (str, bool) ist stabil.
    is_final=False für Stream-Chunks, True für Ende.
    """
    received = []

    def capture(text, is_final):
        received.append((type(text).__name__, type(is_final).__name__, text, is_final))

    chat_widget_for_contract.update_chat_signal.connect(capture)
    chat_widget_for_contract._safe_emit_update("Teil1", False)
    chat_widget_for_contract._safe_emit_update("Teil1Teil2", True)

    assert len(received) == 2
    for type_text, type_bool, _, _ in received:
        assert type_text == "str", "text muss str sein"
        assert type_bool == "bool", "is_final muss bool sein"
    assert received[0][3] is False
    assert received[1][3] is True


@pytest.mark.contract
@pytest.mark.ui
def test_chat_update_signal_required_fields_contract(chat_widget_for_contract):
    """
    Vertrag: Zwei Argumente, beide Pflicht.
    Leerer String für text ist erlaubt (Stream-Start).
    """
    received = []

    def capture(text, is_final):
        received.append((text, is_final))

    chat_widget_for_contract.update_chat_signal.connect(capture)
    chat_widget_for_contract._safe_emit_update("", False)
    chat_widget_for_contract._safe_emit_update("Final", True)

    assert len(received) == 2
    assert received[0] == ("", False)
    assert received[1] == ("Final", True)


@pytest.mark.contract
@pytest.mark.ui
def test_chat_update_signal_ui_reflects_event_payload(chat_widget_for_contract, qtbot):
    """
    UI-Zustand folgt Event-Payload (ui_state_drift-Schutz).

    Verhindert: Event wird emittiert, aber UI zeigt veralteten/falschen Inhalt.
    Prüft die Kette: update_chat_signal → _on_update_chat_slot → on_update_chat → bubble.setText.
    RTB-001: echter Schutz gegen UI-/Event-Zustandsdrift, nicht nur Event-Form.
    """
    widget = chat_widget_for_contract
    widget.add_message("assistant", "Initial")
    qtbot.wait(50)

    # Signal über echte Kette (nicht Mock): emit → slot → on_update_chat → bubble
    widget._safe_emit_update("Aktualisierter Inhalt", True)
    qtbot.wait(50)

    count = widget.conversation_view.message_layout.count()
    assert count >= 1
    last_item = widget.conversation_view.message_layout.itemAt(count - 1)
    assert last_item and last_item.widget()
    bubble_text = last_item.widget().bubble.text()
    assert "Aktualisierter Inhalt" in (bubble_text or ""), (
        f"UI zeigt nicht den Event-Payload. Erwartet: 'Aktualisierter Inhalt', "
        f"bubble.text()={bubble_text!r}"
    )
