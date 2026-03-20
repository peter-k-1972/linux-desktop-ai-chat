"""
ChatMessageBubble – Robuste Message-Komponente für ChatConversationPanel.

Enthält: Rollen-Label + Content (QTextEdit read-only).
- Korrekter Update-Pfad: set_content() → updateGeometry()
- SizePolicy und sizeHint so, dass der volle Text sichtbar ist
- Kontextmenü (Copy, Select All)
- Theme-Integration: Farben aus ThemeManager, keine hardcoded Werte
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QMenu,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QTextOption


def _get_chat_menu_style() -> str:
    """Kontextmenü-Styling aus Theme-Tokens (keine hardcoded Farben)."""
    try:
        from app.gui.themes import get_theme_manager
        t = get_theme_manager().get_tokens()
        bg = t.get("color_bg_surface", "#374151")
        fg = t.get("color_text", "#f3f4f6")
        hover = t.get("color_bg_hover", "#4b5563")
        return f"""
            QMenu {{ background-color: {bg}; color: {fg}; padding: 4px; }}
            QMenu::item:selected {{ background-color: {hover}; }}
        """
    except Exception:
        return """
            QMenu { background-color: #374151; color: #f3f4f6; padding: 4px; }
            QMenu::item:selected { background-color: #4b5563; }
        """


class _MessageContentEdit(QTextEdit):
    """
    Read-only QTextEdit für Nachrichtentext.
    Ruft updateGeometry() bei Textänderung, damit das Layout neu berechnet wird.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("messageContent")
        self.setReadOnly(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setMinimumHeight(0)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def setPlainText(self, text: str) -> None:
        super().setPlainText(text)
        self.updateGeometry()

    def _effective_document_width(self) -> int:
        """
        Liefert eine stabile Breite für die Dokument-Berechnung.
        viewport().width() ist während Layout oft 0 oder falsch → führt zu
        User zu groß (w=1 → riesige Höhe) bzw. Assistant zu klein (w zu groß → wenige Zeilen).
        """
        vw = self.viewport().width()
        if vw >= 100:
            return min(vw, 700)
        parent = self.parent()
        if parent and parent.width() >= 100:
            return min(parent.width() - 48, 700)
        return 400

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = max(1, self.viewport().width())
        self.document().setTextWidth(w)

    def sizeHint(self) -> QSize:
        doc = self.document()
        w = max(100, self._effective_document_width())
        doc.setTextWidth(w)
        h = int(doc.size().height()) + 8
        return QSize(-1, max(24, h))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(_get_chat_menu_style())
        copy_action = menu.addAction("Kopieren")
        copy_action.triggered.connect(self._on_copy)
        copy_full_action = menu.addAction("Komplette Nachricht kopieren")
        copy_full_action.triggered.connect(lambda: self._on_copy_full())
        menu.addSeparator()
        select_all_action = menu.addAction("Alles auswählen")
        select_all_action.triggered.connect(self.selectAll)
        menu.exec(event.globalPos())

    def _on_copy(self):
        from PySide6.QtWidgets import QApplication
        cursor = self.textCursor()
        text = (
            cursor.selectedText().replace("\u2029", "\n")
            if cursor.hasSelection()
            else self.toPlainText()
        )
        if text:
            QApplication.clipboard().setText(text)

    def _on_copy_full(self):
        """Kopiert die komplette Nachricht (Plain Text)."""
        from PySide6.QtWidgets import QApplication
        text = self.toPlainText()
        if text:
            QApplication.clipboard().setText(text)


class ChatMessageBubbleWidget(QFrame):
    """
    Robuste Chat-Nachrichten-Blase: Rolle + Content + optionale Metadaten.

    Primäre Message-Komponente für den Chatbereich (ChatConversationPanel).
    Unterstützt: User, Assistant, Agent; Modell/Agent-Label; Completion-Status-Badge.

    Metadaten-Struktur:
        - role_label: "Du" / "Assistent (model)" / "Agent (name)"
        - _status_badge: Completion-Status (possibly_truncated, interrupted, error)
        - Erweiterbar für optionale Debug-Hinweise

    Verwendung:
        bubble = ChatMessageBubbleWidget(role="assistant", text="...", model="llama3")
        bubble.set_content("neuer Text")  # für Streaming – löst updateGeometry aus
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
        layout.setContentsMargins(12, 12, 12, 12)

        role_text = self._format_role(model, agent)
        role_label = QLabel(role_text)
        role_label.setObjectName("messageRoleLabel")
        layout.addWidget(role_label)

        self._content = _MessageContentEdit()
        self._content.setPlainText(text)
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
        """Anzeige-Label für Completion-Status."""
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
        """Setzt den Completion-Status und aktualisiert das Badge."""
        self._completion_status = completion_status
        self._update_status_badge()

    def set_content(self, text: str) -> None:
        """
        Aktualisiert den Inhalt (Streaming).
        _content.setPlainText → updateGeometry() im Content-Widget.
        Bubble ruft updateGeometry(), damit das Layout die neue Größe (sizeHint) erhält.
        """
        self._content.setPlainText(text)
        self.updateGeometry()

    @property
    def content_widget(self) -> QTextEdit:
        """Für update_last_assistant: direkter Zugriff auf das Content-Widget."""
        return self._content

    def toPlainText(self) -> str:
        """Kompatibilität: Delegation an Content-Widget (für Tests)."""
        return self._content.toPlainText()
