"""
ConversationView – Zentrierte Gesprächsfläche.
Begrenzte Content-Breite, großzügiger Weißraum, saubere Scroll-Fläche.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
)
from PySide6.QtCore import Qt, QTimer

from app.gui.domains.operations.chat.panels.chat_message_widget import ChatMessageWidget


class ConversationView(QWidget):
    """Zentrierte Conversation-Area mit begrenzter Content-Breite."""

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.message_factory = None  # (role, content, timestamp) -> ChatMessageWidget
        self.init_ui()

    def init_ui(self):
        self.setObjectName("conversationView")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Zentrierter Content-Container
        self.content_wrapper = QWidget()
        self.content_wrapper.setObjectName("conversationContentWrapper")
        center_layout = QHBoxLayout(self.content_wrapper)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addStretch(1)
        center_layout.addWidget(self._create_message_container(), 0)
        center_layout.addStretch(1)

        self.scroll_area.setWidget(self.content_wrapper)
        layout.addWidget(self.scroll_area)

    def _create_message_container(self) -> QWidget:
        """Erstellt den zentrierten Nachrichten-Container."""
        self.message_container = QWidget()
        self.message_container.setObjectName("chatContainer")
        self.message_container.setMinimumWidth(1200)
        self.message_container.setMaximumWidth(1200)
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.message_layout.setContentsMargins(32, 40, 32, 40)
        self.message_layout.setSpacing(28)
        return self.message_container

    def set_message_factory(self, factory):
        """Setzt Factory für Message-Widgets: (role, content, timestamp, avatar) -> widget."""
        self.message_factory = factory

    def add_message(self, role: str, content: str, timestamp=None, avatar_path=None):
        """Fügt eine Nachricht hinzu und gibt das Widget zurück."""
        if self.message_factory:
            msg = self.message_factory(role, content, timestamp, avatar_path)
        else:
            msg = ChatMessageWidget(
                role=role,
                content=content,
                timestamp=timestamp,
                theme=self.theme,
                avatar_path=avatar_path,
            )
        self.message_layout.addWidget(msg)
        QTimer.singleShot(50, self.scroll_to_bottom)
        return msg

    def clear(self):
        """Entfernt alle Nachrichten."""
        while self.message_layout.count():
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def scroll_to_bottom(self):
        """Scrollt zum Ende der Conversation."""
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def set_theme(self, theme: str):
        self.theme = theme
