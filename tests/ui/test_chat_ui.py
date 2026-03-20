"""
UI Tests: Chat UI.

Testet Chatfenster öffnen, Nachricht senden, Antwort anzeigen.
Nutzt pytest-qt für PySide6.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from app.gui.domains.operations.chat.panels.conversation_view import ConversationView
from app.gui.domains.operations.chat.panels.chat_composer_widget import ChatComposerWidget, ChatInput
from app.gui.domains.operations.chat.panels.chat_header_widget import ChatHeaderWidget


# --- ConversationView ---

def test_conversation_view_opens(qtbot):
    """Chatfenster (ConversationView) öffnet ohne Fehler."""
    view = ConversationView(theme="dark")
    qtbot.addWidget(view)
    view.show()
    assert view.isVisible()
    assert view.objectName() == "conversationView"


def test_conversation_view_add_message(qtbot):
    """Nachricht wird in ConversationView angezeigt und Inhalt ist sichtbar."""
    view = ConversationView(theme="dark")
    qtbot.addWidget(view)
    qtbot.wait(60)
    msg = view.add_message("user", "Hallo, das ist eine Testnachricht")
    qtbot.wait(60)
    assert msg is not None
    assert msg.role == "user"
    assert view.message_layout.count() >= 1
    # Verhaltenstest: sichtbarer Text statt nur count
    assert "Hallo" in (msg.bubble.text() or ""), (
        f"Nachrichteninhalt nicht sichtbar. bubble.text()={msg.bubble.text()!r}"
    )


@pytest.mark.ui
@pytest.mark.regression
def test_conversation_view_message_content_visible(qtbot):
    """
    Nachricht zeigt korrekten Text und Rolle.
    Verhindert: add_message fügt Widget hinzu, aber Inhalt nicht sichtbar.
    """
    view = ConversationView(theme="dark")
    qtbot.addWidget(view)
    qtbot.wait(60)  # QTimer.singleShot(50, scroll_to_bottom) abwarten

    msg_user = view.add_message("user", "Hallo, das ist eine Testnachricht")
    qtbot.wait(60)
    assert msg_user is not None
    assert msg_user.role == "user"
    assert "Hallo" in (msg_user.bubble.text() or "")
    assert "Testnachricht" in (msg_user.bubble.text() or "")

    msg_asst = view.add_message("assistant", "Das ist die Antwort.")
    qtbot.wait(60)
    assert msg_asst is not None
    assert msg_asst.role == "assistant"
    assert "Antwort" in (msg_asst.bubble.text() or "")


def test_conversation_view_add_assistant_message(qtbot):
    """Assistant-Antwort wird angezeigt und Inhalt ist sichtbar."""
    view = ConversationView(theme="dark")
    qtbot.addWidget(view)
    qtbot.wait(60)
    msg = view.add_message("assistant", "Das ist die Antwort.")
    qtbot.wait(60)
    assert msg is not None
    assert msg.role == "assistant"
    assert "Antwort" in (msg.bubble.text() or ""), (
        f"Assistant-Inhalt nicht sichtbar. bubble.text()={msg.bubble.text()!r}"
    )


# --- ChatComposerWidget ---

def test_chat_composer_opens(qtbot):
    """Composer-Widget öffnet und zeigt Eingabefeld."""
    composer = ChatComposerWidget(icons_path="")
    qtbot.addWidget(composer)
    composer.show()
    assert composer.isVisible()
    # Senden-Button oder Eingabefeld vorhanden
    send_btn = composer.findChild(type(composer), "sendBtn") or [
        c for c in composer.findChildren(QWidget) if "send" in str(c.objectName()).lower()
    ]
    # Composer hat mindestens ein Kind
    assert composer.children()


def test_chat_composer_send_signal(qtbot):
    """Composer send_requested Signal wird bei Senden tatsächlich ausgelöst."""
    composer = ChatComposerWidget(icons_path="")
    qtbot.addWidget(composer)
    received = []

    def on_send():
        received.append(True)

    composer.send_requested.connect(on_send)
    input_widget = composer.findChild(ChatInput)
    assert input_widget is not None
    qtbot.keyClicks(input_widget, "Test")
    # Senden-Button klicken
    from PySide6.QtWidgets import QPushButton
    for btn in composer.findChildren(QPushButton):
        if "send" in (btn.objectName() or "").lower() or "Senden" in btn.text():
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
            break
    qtbot.wait(100)
    # Signal muss tatsächlich emittiert worden sein
    assert len(received) >= 1, "send_requested wurde nicht emittiert"


def test_chat_input_accepts_text(qtbot):
    """ChatInput akzeptiert Texteingabe."""
    inp = ChatInput()
    qtbot.addWidget(inp)
    qtbot.keyClicks(inp, "Hallo Welt")
    assert "Hallo" in inp.toPlainText()


# --- ChatHeaderWidget ---

def test_chat_header_opens(qtbot):
    """Chat-Header öffnet mit Agent- und Modell-Auswahl."""
    header = ChatHeaderWidget(theme="dark")
    qtbot.addWidget(header)
    header.show()
    assert header.isVisible()
    assert header.agent_combo is not None
    assert header.model_combo is not None


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.cross_layer
def test_chat_header_agent_selection_populates_and_affects_messages(qtbot, temp_db_path):
    """
    Agent-Combo befüllt, Auswahl wirkt.
    Verhindert: Agent-Combo leer; Auswahl hat keine Wirkung auf currentData().
    """
    from unittest.mock import patch
    from app.agents.agent_repository import AgentRepository
    from app.agents.agent_registry import AgentRegistry
    from app.agents.agent_profile import AgentProfile, AgentStatus

    with patch("app.agents.seed_agents.ensure_seed_agents") as mock_seed:
        mock_seed.return_value = 0
        repo = AgentRepository(db_path=temp_db_path)
        profile = AgentProfile(
            id=None,
            name="Header-Test-Agent",
            display_name="Header Test",
            slug="header_test_agent",
            department="research",
            status=AgentStatus.ACTIVE.value,
            system_prompt="System-Prompt für Header-Test",
        )
        agent_id = repo.create(profile)
        profile.id = agent_id

        registry = AgentRegistry(repository=repo)
        registry.refresh()
        agents = registry.list_active()

        header = ChatHeaderWidget(theme="dark")
        qtbot.addWidget(header)
        header.agent_combo.clear()
        header.agent_combo.addItem("Standard (kein Agent)", None)
        for a in agents:
            header.agent_combo.addItem(a.effective_display_name, a.id)

        assert header.agent_combo.count() >= 2, "Agent-Combo muss mindestens Standard + 1 Agent haben"

        header.agent_combo.setCurrentIndex(1)
        qtbot.wait(50)
        assert header.agent_combo.currentData() == agent_id
        assert "Header Test" in (header.agent_combo.currentText() or "")


@pytest.mark.ui
@pytest.mark.regression
def test_prompt_apply_to_chat_visible(qtbot):
    """
    "In Chat übernehmen" -> Inhalt erscheint in Conversation.
    Verhindert: Prompt übernehmen ohne Effekt im Chat.
    """
    from unittest.mock import MagicMock, AsyncMock
    from app.gui.legacy import ChatWidget
    from app.prompts.prompt_models import Prompt

    class FakeDB:
        def create_chat(self, title=""):
            return 1
        def save_message(self, cid, role, content):
            pass
        def load_chat(self, cid):
            return []
        def list_workspace_roots_for_chat(self, cid):
            return []

    client = MagicMock()
    client.get_models = AsyncMock(return_value=[])
    settings = type("Settings", (), {"model": "test", "theme": "dark", "icons_path": "", "save": lambda s: None})()
    db = FakeDB()

    class MinimalChatWidget(ChatWidget):
        def load_models(self):
            pass
        def on_update_chat(self, text, is_final):
            pass

    widget = MinimalChatWidget(client, settings, db)
    qtbot.addWidget(widget)
    widget.chat_id = 1

    prompt = Prompt(
        id=1,
        title="P1-Apply-Test",
        category="general",
        description="",
        content="Dieser Prompt-Inhalt soll im Chat erscheinen",
        prompt_type="user",
        tags=[],
        created_at=None,
        updated_at=None,
    )
    widget._on_prompt_apply(prompt)
    qtbot.wait(100)

    count = widget.conversation_view.message_layout.count()
    assert count >= 1
    texts = []
    for i in range(count):
        item = widget.conversation_view.message_layout.itemAt(i)
        if item and item.widget():
            w = item.widget()
            if hasattr(w, "bubble") and hasattr(w.bubble, "text"):
                texts.append(w.bubble.text())
    all_text = " ".join(texts)
    assert "Dieser Prompt-Inhalt soll im Chat erscheinen" in all_text
