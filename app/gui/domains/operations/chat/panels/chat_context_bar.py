"""
ChatContextBar – Kompakte Kontextanzeige im Chat-Bereich.

Zeigt: Projekt, Chat-Titel, optional Topic.
Immer sichtbar, aber nicht dominant.
Labels klickbar für Kontext-Aktionen; Rechtsklick öffnet Kontextmenü.
"""

from typing import Optional

from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal


class _ClickableContextLabel(QPushButton):
    """Klickbarer Kontext-Label (sieht wie Label aus, flacher Button)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("QPushButton { border: none; background: transparent; padding: 0; }")


class ChatContextBar(QFrame):
    """
    Leichte Kontextleiste über dem Nachrichtenbereich.

    Zeigt: [ Projekt: XYZ ] [ Chat: Titel ] [ Topic: optional ]
    Labels klickbar → Projekt wechseln, Chat umbenennen, Topic ändern.
    Rechtsklick → Kontextmenü mit erweiterten Aktionen.
    """

    project_clicked = Signal()
    chat_clicked = Signal()
    topic_clicked = Signal()
    context_menu_requested = Signal()
    """Emit when user right-clicks on the bar; parent shows context menu."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatContextBar")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        self._project_label = _ClickableContextLabel()
        self._project_label.setObjectName("chatContextProject")
        self._project_label.clicked.connect(self.project_clicked.emit)
        layout.addWidget(self._project_label)

        self._chat_label = _ClickableContextLabel()
        self._chat_label.setObjectName("chatContextChat")
        self._chat_label.clicked.connect(self.chat_clicked.emit)
        layout.addWidget(self._chat_label)

        self._topic_label = _ClickableContextLabel()
        self._topic_label.setObjectName("chatContextTopic")
        self._topic_label.clicked.connect(self.topic_clicked.emit)
        layout.addWidget(self._topic_label)

        layout.addStretch()

    def _on_context_menu_requested(self, pos) -> None:
        self.context_menu_requested.emit()

    def set_context(
        self,
        project_name: Optional[str] = None,
        chat_title: Optional[str] = None,
        topic_name: Optional[str] = None,
    ) -> None:
        """
        Setzt den angezeigten Kontext.

        None = leer / Platzhalter.
        """
        if project_name:
            self._project_label.setText(f"Projekt: {project_name}")
            self._project_label.setVisible(True)
        else:
            self._project_label.setText("Projekt: —")
            self._project_label.setVisible(True)

        if chat_title:
            self._chat_label.setText(f"Chat: {chat_title}")
            self._chat_label.setVisible(True)
        else:
            self._chat_label.setText("Chat: —")
            self._chat_label.setVisible(True)

        if topic_name:
            self._topic_label.setText(f"Topic: {topic_name}")
            self._topic_label.setVisible(True)
        else:
            self._topic_label.setVisible(False)

    def clear(self) -> None:
        """Setzt Kontext zurück (kein Chat aktiv)."""
        self.set_context(project_name=None, chat_title=None, topic_name=None)
