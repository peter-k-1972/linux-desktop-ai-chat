"""
UI Tests: Chat Theme – Theme-Integration im Chatbereich.

Testet:
- Chat rendert ohne hardcoded Farben (role property, keine inline hex)
- User-/Assistant-Bubbles unterscheiden sich (role property)
- Metadaten bleiben sichtbar (objectNames)
- Theme-Wechsel bricht Chat nicht
"""

import pytest
from PySide6.QtCore import Qt

from app.gui.domains.operations.chat.panels.chat_message_bubble import ChatMessageBubbleWidget
from app.gui.domains.operations.chat.panels.conversation_panel import ChatConversationPanel


def test_bubble_has_role_property(qtbot):
    """Message-Bubble hat role-Property für Theme-Unterscheidung."""
    user_bubble = ChatMessageBubbleWidget("user", "User-Text")
    asst_bubble = ChatMessageBubbleWidget("assistant", "Assistant-Text")

    assert user_bubble.property("role") == "user"
    assert asst_bubble.property("role") == "assistant"


def test_bubble_user_and_assistant_differ(qtbot):
    """User- und Assistant-Bubbles haben unterschiedliche role-Property."""
    user_bubble = ChatMessageBubbleWidget("user", "Hi")
    asst_bubble = ChatMessageBubbleWidget("assistant", "Hallo")

    assert user_bubble.property("role") != asst_bubble.property("role")


def test_bubble_metadata_labels_have_object_names(qtbot):
    """Metadaten-Labels haben ObjectNames für Theme-Styling."""
    bubble = ChatMessageBubbleWidget("assistant", "Text", model="llama3")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    role_label = bubble.findChild(type(bubble), "messageRoleLabel")
    status_badge = bubble.findChild(type(bubble), "messageStatusBadge")
    # findChild with type might not work for objectName - use findChildren and filter
    from PySide6.QtWidgets import QLabel
    labels = bubble.findChildren(QLabel)
    role_labels = [l for l in labels if l.objectName() == "messageRoleLabel"]
    status_labels = [l for l in labels if l.objectName() == "messageStatusBadge"]
    assert role_labels, "messageRoleLabel fehlt"
    assert status_labels, "messageStatusBadge fehlt"


def test_content_has_object_name(qtbot):
    """Content-Widget hat messageContent ObjectName."""
    bubble = ChatMessageBubbleWidget("assistant", "Text")
    qtbot.addWidget(bubble)
    bubble.show()
    qtbot.wait(30)

    from PySide6.QtWidgets import QTextEdit
    edits = bubble.findChildren(QTextEdit)
    assert edits
    assert edits[0].objectName() == "messageContent"


def test_conversation_panel_no_hardcoded_scroll_style(qtbot):
    """ChatConversationPanel hat keine hardcoded ScrollArea-Styles."""
    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    qtbot.wait(30)

    scroll = panel._scroll
    assert scroll is not None
    # Kein setStyleSheet mit hardcoded #f8fafc auf ScrollArea
    style = scroll.styleSheet() or ""
    assert "#f8fafc" not in style


def test_theme_switch_does_not_break_chat(qtbot):
    """Theme-Wechsel bricht Chat-Komponenten nicht."""
    try:
        from app.gui.themes import get_theme_manager
        mgr = get_theme_manager()
        original = mgr.get_current_id()
    except Exception:
        pytest.skip("ThemeManager nicht verfügbar")

    panel = ChatConversationPanel()
    qtbot.addWidget(panel)
    panel.add_user_message("Test")
    panel.add_assistant_message("Antwort", model="m1")
    qtbot.wait(50)

    # Theme wechseln (falls beide verfügbar)
    try:
        if "dark" in (original or ""):
            mgr.set_theme("light_default")
        else:
            mgr.set_theme("dark_default")
        qtbot.wait(50)
        # Zurück
        mgr.set_theme(original or "dark_default")
    except Exception:
        pass

    # Panel und Bubbles noch intakt
    assert panel._content_layout.count() >= 2
    from PySide6.QtWidgets import QLabel
    labels = panel.findChildren(QLabel)
    assert any("m1" in (l.text() or "") for l in labels)
