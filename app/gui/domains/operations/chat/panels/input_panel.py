"""
ChatInputPanel – Eingabebereich.

Texteingabe, Modellauswahl, Senden-Button, Prompt-Auswahl.
Standard-Control-Höhen (z. B. Modell-Combo): QSS-Owner Theme-``base.qss`` (``QComboBox`` min-height).
Layout/Margins: ``design_metrics``. Ausnahmen: Chat-Zeilenhöhen für Prompt/Senden und QTextEdit (Python-Owner).
"""

from typing import Any, Dict, List, Optional

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

from app.gui.common.model_catalog_combo import apply_catalog_to_combo, combo_current_selection_id
from app.gui.components.markdown_widgets import chat_context_menu_stylesheet
from app.gui.theme import design_metrics as dm


class ChatInputPanel(QFrame):
    """Panel für Chat-Eingabe. Unten im Conversation-Bereich."""

    send_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatInputPanel")
        self._catalog_entries: List[Dict[str, Any]] = []
        self._setup_ui()
        self._model_combo.currentIndexChanged.connect(self._on_model_index_changed)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            dm.CARD_PADDING_PX,
            dm.SPACE_MD_PX,
            dm.CARD_PADDING_PX,
            dm.CARD_PADDING_PX,
        )
        layout.setSpacing(dm.SPACE_SM_PX)

        row_top = QHBoxLayout()
        row_top.setSpacing(dm.FORM_ROW_GAP_PX)

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
        row.setSpacing(dm.FORM_ROW_GAP_PX)

        self._btn_prompt = QPushButton("Prompt")
        self._btn_prompt.setObjectName("promptButton")
        self._btn_prompt.setToolTip("Prompt aus Prompt Studio einfügen")
        self._btn_prompt.setFixedHeight(dm.INPUT_MD_HEIGHT_PX)
        self._btn_prompt.clicked.connect(self._on_prompt_clicked)
        row.addWidget(self._btn_prompt, 0, Qt.AlignmentFlag.AlignBottom)

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
        self._btn_send.setFixedHeight(dm.CHAT_PRIMARY_SEND_HEIGHT_PX)
        self._btn_send.clicked.connect(self._on_send)
        row.addWidget(self._btn_send, 0, Qt.AlignmentFlag.AlignBottom)

        layout.addLayout(row)

    def _on_input_context_menu(self, pos):
        """Rechtsklick-Kontextmenü: Ausschneiden, Kopieren, Einfügen, Alles auswählen."""
        menu = QMenu(self)
        menu.setStyleSheet(chat_context_menu_stylesheet())
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
        menu.setStyleSheet(chat_context_menu_stylesheet())

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

    def set_unified_catalog(
        self, entries: List[Dict[str, Any]], default_selection_id: str | None = None
    ) -> None:
        """Setzt die Modellliste aus dem Unified-Katalog (Tooltips, deaktivierte Zeilen)."""
        self._catalog_entries = list(entries)
        apply_catalog_to_combo(
            self._model_combo,
            entries,
            default_selection_id=default_selection_id,
        )

    def set_models(self, model_names: list[str], default: str | None = None) -> None:
        """Abwärtskompatibel: nur Namen, alle Einträge als runtime-fähig markiert."""
        current = self.get_selected_model()
        entries: List[Dict[str, Any]] = []
        for n in model_names:
            nn = (n or "").strip()
            if not nn:
                continue
            entries.append(
                {
                    "selection_id": nn,
                    "display_short": nn,
                    "display_detail": "",
                    "chat_selectable": True,
                    "source_kind": "legacy_list",
                    "is_online": False,
                    "runtime_ready": True,
                    "has_local_asset": False,
                    "registry_id": nn,
                    "ollama_size": None,
                    "asset_id": None,
                    "storage_root_name": "",
                    "path_hint": "",
                    "assignment_state": "none",
                    "asset_available": None,
                    "asset_type": "",
                    "usage_summary": "",
                    "quota_summary": "",
                    "usage_quality_note": "",
                }
            )
        pick_default = default
        if current and any(e["selection_id"] == current for e in entries):
            pick_default = current
        self.set_unified_catalog(entries, default_selection_id=pick_default)

    def _on_model_index_changed(self, _idx: int) -> None:
        """Sichert, dass kein deaktivierter Eintrag aktiv bleibt (Fallback)."""
        from app.gui.common.model_catalog_combo import combo_selection_blocked

        if combo_selection_blocked(self._model_combo):
            self._model_combo.blockSignals(True)
            m = self._model_combo.model()
            if hasattr(m, "rowCount"):
                for i in range(m.rowCount()):
                    it = m.item(i)
                    if it and it.isEnabled():
                        self._model_combo.setCurrentIndex(i)
                        break
            self._model_combo.blockSignals(False)
        self._refresh_model_context_line()

    def refresh_model_ancillary_display(self) -> None:
        """Nach Katalog-Reload: Usage/Quota-Zeile zum gewählten Modell aktualisieren."""
        self._refresh_model_context_line()

    def _refresh_model_context_line(self) -> None:
        """Kompakte Modell-Zusatzinfos (Usage/Quota) in der Statuszeile neben der Combo."""
        sid = combo_current_selection_id(self._model_combo)
        if not sid:
            self.set_status("")
            return
        for e in self._catalog_entries:
            if e.get("selection_id") != sid:
                continue
            parts: list[str] = []
            for key in ("usage_summary", "quota_summary", "usage_quality_note"):
                s = (e.get(key) or "").strip()
                if s and s != "—":
                    parts.append(s)
            if parts:
                line = " · ".join(parts)
                if len(line) > 220:
                    line = line[:217] + "…"
                self.set_status(line)
            else:
                self.set_status("")
            return
        self.set_status("")

    def get_selected_model(self) -> str | None:
        """Liefert die gewählte Modell-ID, wenn der Eintrag für Chat nutzbar ist."""
        sid = combo_current_selection_id(self._model_combo)
        if sid:
            return sid
        m = self._model_combo.model()
        if hasattr(m, "rowCount") and m.rowCount() == 0:
            return None
        return self._model_combo.currentText().strip() or None

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
