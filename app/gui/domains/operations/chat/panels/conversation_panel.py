"""
ChatConversationPanel – Nachrichtenbereich.

Scrollbarer Verlauf. User/Assistant getrennt. Lädt aus DB, unterstützt Streaming.
Nutzt ChatMessageBubbleWidget als robuste Message-Komponente.
"""

from PySide6.QtWidgets import (
    QVBoxLayout,
    QScrollArea,
    QFrame,
    QWidget,
)
from PySide6.QtCore import Qt

from app.gui.domains.operations.chat.panels.chat_message_bubble import ChatMessageBubbleWidget


class ChatConversationPanel(QFrame):
    """Panel für den Chat-Verlauf. Zentrale Mitte."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatConversationPanel")
        self._setup_ui()
        self._last_assistant_bubble: ChatMessageBubbleWidget | None = None

    def clear(self) -> None:
        """Entfernt alle Nachrichten."""
        while self._content_layout.count() > 1:
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._last_assistant_bubble = None

    def load_messages(self, messages: list) -> None:
        """Lädt Nachrichten. messages: [(role, content, timestamp), ...] oder [(role, content, ts, model?, agent?, completion_status?), ...]"""
        self.clear()
        for row in messages:
            role = row[0]
            content = row[1] if len(row) > 1 else ""
            model = row[3] if len(row) > 3 else None
            agent = row[4] if len(row) > 4 else None
            completion_status = row[5] if len(row) > 5 else None
            self._add_message(
                role, content, model=model, agent=agent, completion_status=completion_status
            )

    def add_user_message(self, text: str) -> None:
        """Fügt eine Benutzer-Nachricht hinzu."""
        self._add_message("user", text)

    def add_assistant_message(
        self,
        text: str,
        *,
        model: str | None = None,
        agent: str | None = None,
        completion_status: str | None = None,
    ) -> None:
        """Fügt eine Assistenten-Nachricht hinzu."""
        self._add_message(
            "assistant",
            text,
            model=model,
            agent=agent,
            completion_status=completion_status,
        )

    def add_assistant_placeholder(
        self,
        *,
        model: str | None = None,
        agent: str | None = None,
    ) -> ChatMessageBubbleWidget:
        """Fügt Platzhalter für Streaming hinzu. Gibt die Bubble zurück für Updates."""
        bubble = ChatMessageBubbleWidget("assistant", "...", model=model, agent=agent)
        self._content_layout.insertWidget(self._content_layout.count() - 1, bubble)
        self._last_assistant_bubble = bubble
        return bubble

    def update_last_assistant(self, text: str) -> None:
        """Aktualisiert die letzte Assistenten-Nachricht (für Streaming). Löst updateGeometry aus."""
        if self._last_assistant_bubble:
            self._last_assistant_bubble.set_content(text)
            self._content_layout.invalidate()

    def set_last_assistant_completion_status(
        self, completion_status: str | None
    ) -> None:
        """Setzt den Completion-Status der letzten Assistenten-Nachricht (Badge)."""
        if self._last_assistant_bubble:
            self._last_assistant_bubble.set_completion_status(completion_status)

    def finalize_streaming(self) -> None:
        """Markiert Streaming als beendet."""
        self._last_assistant_bubble = None

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(20, 20, 20, 20)
        self._content_layout.setSpacing(16)
        self._content_layout.addStretch()

        self._scroll.setWidget(self._content)
        layout.addWidget(self._scroll)

    def _add_message(
        self,
        role: str,
        text: str,
        *,
        model: str | None = None,
        agent: str | None = None,
        completion_status: str | None = None,
    ) -> None:
        """Fügt eine Nachricht hinzu."""
        bubble = ChatMessageBubbleWidget(
            role, text, model=model, agent=agent, completion_status=completion_status
        )
        self._content_layout.insertWidget(self._content_layout.count() - 1, bubble)
        if role == "assistant":
            self._last_assistant_bubble = None

    def scroll_to_bottom(self) -> None:
        """Scrollt zum unteren Rand."""
        scrollbar = self._scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
