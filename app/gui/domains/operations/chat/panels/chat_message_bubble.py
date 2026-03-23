"""
ChatMessageBubble – Robuste Message-Komponente für ChatConversationPanel.

Enthält: Rollen-Label + MarkdownMessageWidget (zentrale Pipeline).
- set_content() → MarkdownMessageWidget.set_markdown → updateGeometry()
- Theme: #messageBubble #messageContent (ObjectName am Content-Widget)
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
)

from app.gui.components.markdown_widgets import MarkdownMessageWidget
from app.gui.theme import design_metrics as dm


class ChatMessageBubbleWidget(QFrame):
    """
    Robuste Chat-Nachrichten-Blase: Rolle + Content + optionale Metadaten.

    Primäre Message-Komponente für den Chatbereich (ChatConversationPanel).
    Unterstützt: User, Assistant, Agent; Modell/Agent-Label; Completion-Status-Badge.
    """

    def __init__(
        self,
        role: str,
        text: str,
        *,
        model: str | None = None,
        agent: str | None = None,
        completion_status: str | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("messageBubble")
        self._role = role
        self._is_user = role == "user"
        self._completion_status = completion_status
        self._setup_ui(text, model, agent)

    def _setup_ui(self, text: str, model: str | None, agent: str | None) -> None:
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setProperty("role", "user" if self._is_user else "assistant")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            dm.SPACE_MD_PX,
            dm.SPACE_MD_PX,
            dm.SPACE_MD_PX,
            dm.SPACE_MD_PX,
        )

        role_text = self._format_role(model, agent)
        role_label = QLabel(role_text)
        role_label.setObjectName("messageRoleLabel")
        layout.addWidget(role_label)

        self._content = MarkdownMessageWidget()
        self._content.setObjectName("messageContent")
        self._content.set_markdown(text or "")
        layout.addWidget(self._content)

        self._status_badge = QLabel()
        self._status_badge.setObjectName("messageStatusBadge")
        self._status_badge.setWordWrap(True)
        layout.addWidget(self._status_badge)
        self._update_status_badge()

    def _format_role(self, model: str | None, agent: str | None) -> str:
        if self._is_user:
            return "Du"
        if agent:
            return f"Agent ({agent})"
        if model:
            return f"Assistent ({model})"
        return "Assistent (unbekanntes Modell)"

    def _status_label(self, status: str | None) -> str:
        if not status or status == "complete":
            return ""
        labels = {
            "possibly_truncated": "möglicherweise unvollständig",
            "interrupted": "Antwort unterbrochen",
            "error": "Generierung beendet mit Fehler",
        }
        return labels.get(status, "")

    def _update_status_badge(self) -> None:
        label = self._status_label(self._completion_status)
        self._status_badge.setText(label)
        self._status_badge.setVisible(bool(label))

    def set_completion_status(self, completion_status: str | None) -> None:
        self._completion_status = completion_status
        self._update_status_badge()

    def set_content(self, text: str) -> None:
        """Streaming-Update: zentrale Markdown-Pipeline."""
        self._content.set_markdown(text or "")
        self.updateGeometry()

    @property
    def content_widget(self) -> MarkdownMessageWidget:
        return self._content

    def toPlainText(self) -> str:
        return self._content.toPlainText()
