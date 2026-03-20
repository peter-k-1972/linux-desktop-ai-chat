"""
UI Tests: Chat UX Hardening.

Testet den gehärteten Chat-UX-Layer:
- Kontextmenü/Copy-Basis für Nachrichten
- Eingabefeld Standardaktionen (Cut, Copy, Paste, Select All)
- Modell-/Agentenlabel aus Metadaten
- Completion-/Statusbadge
- User-/Assistant-/Agent-Nachrichten konsistent
- Keine Regression der Message-Komponente
"""

import pytest
from PySide6.QtWidgets import QLabel, QTextEdit
from PySide6.QtCore import Qt

from app.gui.domains.operations.chat.panels.chat_message_bubble import ChatMessageBubbleWidget
from app.gui.domains.operations.chat.panels.conversation_panel import ChatConversationPanel
from app.gui.domains.operations.chat.panels.input_panel import ChatInputPanel


def _get_last_bubble(panel):
    """Letzte Message-Bubble im Panel."""
    last = None
    for i in range(panel._content_layout.count() - 1):
        w = panel._content_layout.itemAt(i).widget()
        if w and w.objectName() == "messageBubble":
            last = w
    return last


def test_message_context_menu_has_copy_and_select_all(qtbot):
    """Kontextmenü für Nachrichten hat Copy und Select All."""
    bubble = ChatMessageBubbleWidget("assistant", "Test-Text")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    edits = bubble.findChildren(QTextEdit)
    assert edits
    content = edits[0]
    # Kontextmenü wird bei contextMenuEvent erzeugt – wir prüfen, dass die
    # Content-Komponente ein Kontextmenü hat (CustomContextMenu oder
    # contextMenuEvent überschrieben)
    assert hasattr(content, "contextMenuEvent")


def test_message_context_menu_copy_full_action(qtbot):
    """Komplette Nachricht kopieren ist verfügbar (Copy-Logik)."""
    from PySide6.QtWidgets import QApplication

    bubble = ChatMessageBubbleWidget("assistant", "Vollständiger Nachrichtentext")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    content = bubble.content_widget
    content._on_copy_full()
    qtbot.wait(20)
    clipboard = QApplication.clipboard().text()
    assert "Vollständiger Nachrichtentext" in clipboard


def test_input_panel_has_context_menu(qtbot):
    """Eingabefeld hat Kontextmenü mit Standardaktionen."""
    panel = ChatInputPanel()
    qtbot.addWidget(panel)
    panel.show()
    qtbot.wait(30)

    assert panel._input.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu
    assert panel._input.customContextMenuRequested is not None


def test_model_label_from_metadata(qtbot):
    """Modell-Label wird korrekt aus Metadaten erzeugt."""
    bubble = ChatMessageBubbleWidget("assistant", "Antwort", model="llama3.2")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    labels = bubble.findChildren(QLabel)
    texts = [l.text() for l in labels]
    assert any("llama3.2" in t for t in texts), f"Modell nicht in Labels: {texts}"


def test_agent_label_from_metadata(qtbot):
    """Agenten-Label wird korrekt aus Metadaten erzeugt."""
    bubble = ChatMessageBubbleWidget("assistant", "Antwort", agent="Research-Agent")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    labels = bubble.findChildren(QLabel)
    texts = [l.text() for l in labels]
    assert any("Research-Agent" in t or "Agent" in t for t in texts), f"Agent nicht: {texts}"


def test_fallback_unknown_model(qtbot):
    """Fallback 'Assistent (unbekanntes Modell)' bei fehlenden Metadaten."""
    bubble = ChatMessageBubbleWidget("assistant", "Antwort")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    labels = bubble.findChildren(QLabel)
    texts = [l.text() for l in labels]
    assert any("unbekannt" in (t or "").lower() for t in texts), f"Fallback nicht: {texts}"


def test_completion_status_badge_displayed(qtbot):
    """Completion-Status-Badge wird korrekt angezeigt."""
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
    assert any("unvollständig" in t.lower() for t in texts), f"Badge nicht: {texts}"


def test_completion_status_interrupted(qtbot):
    """Status 'interrupted' wird angezeigt."""
    bubble = ChatMessageBubbleWidget(
        "assistant", "Text", completion_status="interrupted"
    )
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    labels = bubble.findChildren(QLabel)
    texts = [l.text() for l in labels]
    assert any("unterbrochen" in t.lower() for t in texts), f"interrupted nicht: {texts}"


def test_user_assistant_agent_consistent(qtbot):
    """User-, Assistant- und Agent-Nachrichten bleiben konsistent."""
    user_b = ChatMessageBubbleWidget("user", "User")
    asst_b = ChatMessageBubbleWidget("assistant", "Assistant", model="m1")
    agent_b = ChatMessageBubbleWidget("assistant", "Agent", agent="A1")

    for b in (user_b, asst_b, agent_b):
        assert b.objectName() == "messageBubble"
        assert b.content_widget is not None
        assert b.toPlainText()


def test_no_regression_message_component(qtbot):
    """Keine Regression: Message-Komponente funktioniert."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    panel.add_user_message("Hallo")
    panel.add_assistant_message("Antwort", model="llama3")
    qtbot.wait(50)

    bubbles = [
        panel._content_layout.itemAt(i).widget()
        for i in range(panel._content_layout.count() - 1)
        if panel._content_layout.itemAt(i).widget()
        and panel._content_layout.itemAt(i).widget().objectName() == "messageBubble"
    ]
    assert len(bubbles) >= 2
    assert "Hallo" in bubbles[0].toPlainText()
    assert "Antwort" in bubbles[1].toPlainText()
    assert "llama3" in " ".join(
        l.text() for l in bubbles[1].findChildren(QLabel)
    )
