"""
UI Tests: Chat Message Rendering – vereinheitlichte Architektur.

Testet die primäre Message-Komponente (ChatMessageBubbleWidget) und
ChatConversationPanel auf:
- Lange/kurze Nachrichten
- User vs. Assistant gleiche Grundregeln
- Metadaten (Rolle, Modell, Agent, Status)
- Keine Regression beim Chat-Rendering
- Keine Fixed-/Pseudo-Fixed-Height-Rückfälle
"""

import pytest
from PySide6.QtWidgets import QLabel, QTextEdit, QSizePolicy
from PySide6.QtCore import Qt

from app.gui.domains.operations.chat.panels.chat_message_bubble import ChatMessageBubbleWidget
from app.gui.domains.operations.chat.panels.conversation_panel import ChatConversationPanel


def _get_bubbles(panel):
    """Hilfe: alle Message-Bubbles im Panel."""
    bubbles = []
    for i in range(panel._content_layout.count() - 1):
        item = panel._content_layout.itemAt(i)
        if item and item.widget() and item.widget().objectName() == "messageBubble":
            bubbles.append(item.widget())
    return bubbles


def test_bubble_short_message_compact(qtbot):
    """Kurze Nachricht bleibt kompakt (keine unnötige Expansion)."""
    bubble = ChatMessageBubbleWidget("user", "Kurz")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(50)

    policy = bubble.sizePolicy()
    assert policy.verticalPolicy() == QSizePolicy.Policy.Minimum
    assert bubble.toPlainText() == "Kurz"


def test_bubble_long_message_full_content(qtbot):
    """Lange Nachricht wird vollständig dargestellt."""
    long_text = "Absatz 1.\n\n" + "Zeile " * 80 + "\n\n" + "Absatz Ende."
    bubble = ChatMessageBubbleWidget("assistant", long_text)
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(50)

    content = bubble.toPlainText()
    assert "Absatz 1" in content
    assert "Absatz Ende" in content
    assert "Zeile" in content


def test_bubble_user_and_assistant_same_rules(qtbot):
    """User- und Assistant-Nachricht folgen denselben Grundregeln (SizePolicy, Struktur)."""
    user_bubble = ChatMessageBubbleWidget("user", "User-Text")
    asst_bubble = ChatMessageBubbleWidget("assistant", "Assistant-Text")

    for b in (user_bubble, asst_bubble):
        policy = b.sizePolicy()
        assert policy.verticalPolicy() == QSizePolicy.Policy.Minimum
        assert policy.horizontalPolicy() == QSizePolicy.Policy.Expanding
        assert b.objectName() == "messageBubble"
        assert b.content_widget is not None


def test_bubble_metadata_role_model(qtbot):
    """Message-Komponente zeigt Metadaten (Rolle, Modell)."""
    bubble = ChatMessageBubbleWidget("assistant", "Antwort", model="llama3.2")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    labels = bubble.findChildren(QLabel)
    texts = [l.text() for l in labels]
    assert any("llama3.2" in t for t in texts), f"Modell nicht in Labels: {texts}"


def test_bubble_metadata_agent(qtbot):
    """Message-Komponente zeigt Agent-Metadaten."""
    bubble = ChatMessageBubbleWidget("assistant", "Agent-Antwort", agent="Research")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    labels = bubble.findChildren(QLabel)
    texts = [l.text() for l in labels]
    assert any("Research" in t or "Agent" in t for t in texts), f"Agent nicht in Labels: {texts}"


def test_bubble_completion_status_badge(qtbot):
    """Message-Komponente zeigt Completion-Status-Badge."""
    bubble = ChatMessageBubbleWidget(
        "assistant", "Text", completion_status="possibly_truncated"
    )
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    labels = bubble.findChildren(QLabel)
    texts = [l.text() for l in labels]
    assert any("unvollständig" in t.lower() for t in texts), f"Badge nicht gefunden: {texts}"


def test_bubble_set_content_updates(qtbot):
    """set_content aktualisiert Inhalt und löst updateGeometry aus."""
    bubble = ChatMessageBubbleWidget("assistant", "...")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    bubble.set_content("Neuer langer Text für Streaming")
    qtbot.wait(30)

    assert "Neuer langer Text" in bubble.toPlainText()


def test_bubble_text_selectable(qtbot):
    """Text ist auswählbar (Copy/Selection-Basis)."""
    bubble = ChatMessageBubbleWidget("assistant", "Kopierbar")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    edits = bubble.findChildren(QTextEdit)
    assert edits
    flags = edits[0].textInteractionFlags()
    assert bool(flags & Qt.TextInteractionFlag.TextSelectableByMouse)


def test_conversation_panel_long_message_rendered(qtbot):
    """Lange Nachricht im Panel vollständig dargestellt (keine Regression)."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    panel.show()
    qtbot.wait(50)

    long_text = "Start.\n\n" + "Zeile " * 60 + "\n\n" + "Ende."
    panel.add_assistant_message(long_text)
    qtbot.wait(100)

    bubbles = _get_bubbles(panel)
    assert bubbles
    content = bubbles[-1].toPlainText()
    assert "Start" in content
    assert "Ende" in content


def test_conversation_panel_short_message_compact(qtbot):
    """Kurze Nachricht im Panel bleibt kompakt."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    qtbot.wait(50)

    panel.add_user_message("Hi")
    panel.add_assistant_message("Hallo")
    qtbot.wait(50)

    bubbles = _get_bubbles(panel)
    assert len(bubbles) >= 2
    assert bubbles[-1].toPlainText() == "Hallo"


def test_conversation_panel_no_fixed_height(qtbot):
    """Keine Fixed-/Pseudo-Fixed-Height auf Message-Komponenten."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    panel.add_assistant_message("Test")
    qtbot.wait(50)

    bubbles = _get_bubbles(panel)
    assert bubbles
    b = bubbles[-1]
    # Kein setFixedHeight, kein setMaximumHeight auf Content
    content = b.content_widget
    assert content.maximumHeight() == 16777215  # QWIDGETSIZE_MAX, default
    assert content.minimumHeight() == 0
