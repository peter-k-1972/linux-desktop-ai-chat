"""
UI Tests: Chat-Härtung (ChatConversationPanel, Rendering, Copy, Modell-Label).

Testet:
- Vollständige Anzeige langer Texte
- Kontextmenü/Copy-Funktionen
- Modell-/Agentenkennzeichnung pro Antwort
"""

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QTextEdit
from PySide6.QtCore import Qt

from app.gui.domains.operations.chat.panels.conversation_panel import ChatConversationPanel


def _get_last_bubble(panel):
    """Hilfe: letzte Message-Bubble im Panel."""
    last = None
    for i in range(panel._content_layout.count() - 1):
        w = panel._content_layout.itemAt(i).widget()
        if w and w.objectName() == "messageBubble":
            last = w
    return last


def test_conversation_panel_opens(qtbot):
    """ChatConversationPanel öffnet ohne Fehler."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    panel.show()
    assert panel.isVisible()
    assert panel.objectName() == "chatConversationPanel"


def test_conversation_panel_add_user_message(qtbot):
    """Benutzer-Nachricht wird angezeigt."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    qtbot.wait(50)
    panel.add_user_message("Hallo, Testnachricht")
    qtbot.wait(50)
    assert panel._content_layout.count() >= 2  # Nachricht + Stretch


def test_conversation_panel_long_text_rendered(qtbot):
    """
    Lange Antworten werden vollständig angezeigt.
    Verhindert: stilles Abschneiden von Chatantworten.
    """
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    panel.show()
    qtbot.wait(50)

    long_text = "Erster Absatz.\n\n" + "Zeile " * 50 + "\n\n" + "Weiterer Inhalt am Ende."
    panel.add_assistant_message(long_text)
    qtbot.wait(100)

    bubble = _get_last_bubble(panel)
    assert bubble is not None
    text_edits = bubble.findChildren(QTextEdit)
    assert text_edits
    content = text_edits[0].toPlainText()
    assert "Erster Absatz" in content
    assert "Weiterer Inhalt am Ende" in content


def test_conversation_panel_streaming_updates(qtbot):
    """Streaming-Placeholder wird korrekt aktualisiert."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    qtbot.wait(50)

    widget = panel.add_assistant_placeholder()
    qtbot.wait(50)
    assert widget is not None

    panel.update_last_assistant("Teil 1")
    qtbot.wait(30)
    assert "Teil 1" in widget.toPlainText()

    panel.update_last_assistant("Teil 1 und Teil 2")
    qtbot.wait(30)
    assert "Teil 2" in widget.toPlainText()

    panel.finalize_streaming()
    assert panel._last_assistant_bubble is None


def test_conversation_panel_model_label(qtbot):
    """Modell-Label wird bei Assistant-Nachricht angezeigt."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    qtbot.wait(50)

    panel.add_assistant_message("Antwort", model="llama3.2")
    qtbot.wait(50)

    bubble = _get_last_bubble(panel)
    assert bubble is not None
    labels = bubble.findChildren(QLabel)
    role_texts = [l.text() for l in labels]
    assert any("llama3.2" in t for t in role_texts), f"Modell nicht in Labels: {role_texts}"


def test_conversation_panel_agent_label(qtbot):
    """Agent-Label wird bei Agenten-Antwort angezeigt."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    qtbot.wait(50)

    panel.add_assistant_message("Agent-Antwort", agent="Research-Agent")
    qtbot.wait(50)

    bubble = _get_last_bubble(panel)
    assert bubble is not None
    labels = bubble.findChildren(QLabel)
    role_texts = [l.text() for l in labels]
    assert any("Research-Agent" in t or "Agent" in t for t in role_texts), f"Agent nicht in Labels: {role_texts}"


def test_conversation_panel_load_messages_extended_format(qtbot):
    """load_messages akzeptiert erweitertes Format (role, content, ts, model, agent)."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    qtbot.wait(50)

    messages = [
        ("user", "Hallo", "2024-01-01 12:00:00"),
        ("assistant", "Antwort", "2024-01-01 12:00:01", "llama3.2", None),
    ]
    panel.load_messages(messages)
    qtbot.wait(50)

    assert panel._content_layout.count() >= 3  # 2 Nachrichten + Stretch


def test_conversation_panel_completion_status_badge(qtbot):
    """Completion-Status-Badge wird bei possibly_truncated angezeigt."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    qtbot.wait(50)

    panel.add_assistant_message(
        "Unvollständige Antwort",
        completion_status="possibly_truncated",
    )
    qtbot.wait(50)

    bubble = _get_last_bubble(panel)
    assert bubble is not None
    labels = bubble.findChildren(QLabel)
    texts = [l.text() for l in labels]
    assert any("unvollständig" in t.lower() for t in texts), f"Badge nicht gefunden: {texts}"


def test_conversation_panel_text_selectable(qtbot):
    """Text in Nachrichten ist auswählbar (TextSelectableByMouse)."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    panel.add_assistant_message("Kopierbarer Text")
    qtbot.wait(50)

    bubble = _get_last_bubble(panel)
    assert bubble is not None
    text_edits = bubble.findChildren(QTextEdit)
    assert text_edits
    flags = text_edits[0].textInteractionFlags()
    assert bool(flags & Qt.TextInteractionFlag.TextSelectableByMouse)
