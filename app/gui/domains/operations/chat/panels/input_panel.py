"""
ChatInputPanel – Eingabebereich.

Texteingabe, Modellauswahl, Senden-Button, Prompt-Auswahl.
Theme-Integration: Farben aus shell.qss, keine hardcoded Werte.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QFrame,
    QComboBox,
    QMenu,
)
from PySide6.QtCore import Qt, Signal, QEvent, QTimer
from PySide6.QtGui import QKeyEvent, QCursor

from app.gui.domains.operations.chat.panels.chat_message_bubble import _get_chat_menu_style


class ChatInputPanel(QFrame):
    """Panel für Chat-Eingabe. Unten im Conversation-Bereich."""

    send_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatInputPanel")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(8)

        row_top = QHBoxLayout()
        row_top.setSpacing(12)

        model_label = QLabel("Modell:")
        model_label.setObjectName("modelLabel")
        row_top.addWidget(model_label)

        self._model_combo = QComboBox()
        self._model_combo.setObjectName("modelCombo")
        self._model_combo.setMinimumWidth(180)
        self._model_combo.setEditable(False)
        row_top.addWidget(self._model_combo)

        self._status_label = QLabel("")
        self._status_label.setObjectName("statusLabel")
        row_top.addWidget(self._status_label, 1)

        layout.addLayout(row_top)

        row = QHBoxLayout()
        row.setSpacing(12)

        self._btn_prompt = QPushButton("Prompt")
        self._btn_prompt.setObjectName("promptButton")
        self._btn_prompt.setToolTip("Prompt aus Prompt Studio einfügen")
        self._btn_prompt.setFixedHeight(48)
        self._btn_prompt.clicked.connect(self._on_prompt_clicked)
        row.addWidget(self._btn_prompt)

        self._input = QTextEdit()
        self._input.setObjectName("chatInput")
        self._input.setPlaceholderText("Nachricht eingeben... (Strg+Enter zum Senden)")
        self._input.setMaximumHeight(120)
        self._input.setMinimumHeight(60)
        self._input.installEventFilter(self)
        self._input.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._input.customContextMenuRequested.connect(self._on_input_context_menu)
        row.addWidget(self._input, 1)

        self._btn_send = QPushButton("Senden")
        self._btn_send.setObjectName("sendButton")
        self._btn_send.setFixedHeight(48)
        self._btn_send.clicked.connect(self._on_send)
        row.addWidget(self._btn_send)

        layout.addLayout(row)

    def _on_input_context_menu(self, pos):
        """Rechtsklick-Kontextmenü: Ausschneiden, Kopieren, Einfügen, Alles auswählen."""
        menu = QMenu(self)
        menu.setStyleSheet(_get_chat_menu_style())
        cut_action = menu.addAction("Ausschneiden")
        cut_action.triggered.connect(self._input.cut)
        cut_action.setEnabled(not self._input.isReadOnly())
        copy_action = menu.addAction("Kopieren")
        copy_action.triggered.connect(self._input.copy)
        copy_action.setEnabled(self._input.textCursor().hasSelection())
        paste_action = menu.addAction("Einfügen")
        paste_action.triggered.connect(self._input.paste)
        paste_action.setEnabled(not self._input.isReadOnly())
        menu.addSeparator()
        select_all_action = menu.addAction("Alles auswählen")
        select_all_action.triggered.connect(self._input.selectAll)
        menu.exec(self._input.mapToGlobal(pos))

    def eventFilter(self, obj, event):
        """Strg+Enter sendet."""
        if obj is self._input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._on_send()
                return True
        return super().eventFilter(obj, event)

    def _on_send(self):
        text = self._input.toPlainText().strip()
        if text:
            self.send_requested.emit(text)
            self._input.clear()

    def _on_prompt_clicked(self) -> None:
        """Öffnet Auswahlmenü für Prompts aus dem Prompt Studio."""
        try:
            from app.prompts.prompt_service import get_prompt_service

            svc = get_prompt_service()
            prompts = svc.list_all()
        except Exception:
            prompts = []

        menu = QMenu(self)
        menu.setObjectName("chatPromptMenu")
        menu.setStyleSheet(_get_chat_menu_style())

        if not prompts:
            action = menu.addAction("Keine Prompts verfügbar")
            action.setEnabled(False)
        else:
            for p in prompts:
                title = (p.title or "Unbenannt").strip() or "Unbenannt"
                content = (p.content or "").strip()
                action = menu.addAction(title)
                action.setEnabled(bool(content))
                if content:
                    action.triggered.connect(
                        lambda checked=False, t=content: self._insert_prompt_text(t)
                    )

        menu.exec(QCursor.pos())

    def _insert_prompt_text(self, text: str) -> None:
        """Fügt Prompt-Inhalt ins Eingabefeld ein. Kein Auto-Send."""
        if not text:
            return
        current = self._input.toPlainText()
        if current:
            self._input.setPlainText(current + "\n\n" + text)
        else:
            self._input.setPlainText(text)
        self._input.setFocus()

    def set_models(self, model_names: list[str], default: str | None = None) -> None:
        """Setzt die Modell-Liste. default: bevorzugtes Modell (z.B. aus get_default_chat_model)."""
        current = self.get_selected_model()
        self._model_combo.clear()
        self._model_combo.addItems(model_names)
        if current and current in model_names:
            self._model_combo.setCurrentText(current)
        elif default and default in model_names:
            self._model_combo.setCurrentText(default)
        else:
            try:
                from app.services.model_service import get_model_service
                fallback = get_model_service().get_default_model()
                if fallback and fallback in model_names:
                    self._model_combo.setCurrentText(fallback)
                    return
            except Exception:
                pass
            if model_names:
                self._model_combo.setCurrentIndex(0)

    def get_selected_model(self) -> str | None:
        """Liefert das aktuell gewählte Modell."""
        text = self._model_combo.currentText().strip()
        return text or None

    def set_status(self, text: str) -> None:
        """Setzt den Status-Text."""
        self._status_label.setText(text)
        self._status_label.setProperty("error", "false")
        self._refresh_status_style()

    def set_error(self, msg: str) -> None:
        """Zeigt eine Fehlermeldung als Inline-Warnung (nicht als Chat-Nachricht)."""
        self._status_label.setText(msg)
        self._status_label.setProperty("error", "true")
        self._refresh_status_style()
        QTimer.singleShot(5000, lambda: self.set_status(""))

    def _refresh_status_style(self) -> None:
        """Aktualisiert Style nach Property-Änderung (error true/false)."""
        try:
            style = self._status_label.style()
            style.unpolish(self._status_label)
            style.polish(self._status_label)
        except Exception:
            pass

    def set_sending(self, sending: bool) -> None:
        """Deaktiviert Eingabe während des Sendens."""
        self._btn_send.setEnabled(not sending)
        self._input.setEnabled(not sending)
        if sending:
            self.set_status("Antwort wird geladen…")
        else:
            self.set_status("")
