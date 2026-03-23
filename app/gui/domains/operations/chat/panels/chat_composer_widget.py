"""
ChatComposerWidget – Moderner Composer-Bereich unten.
Großes Eingabefeld, Senden-Button, Slash-Command-Hinweis.
"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QLabel,
)
from PySide6.QtCore import Qt, Signal, QSize
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.help.tooltip_helper import get_tooltip
from app.gui.theme import design_metrics as dm


class ChatInput(QPlainTextEdit):
    """Eingabefeld mit dynamischer Höhe und Return-to-Send."""

    returnPressed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Nachricht eingeben…")
        self.setFrameStyle(0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.textChanged.connect(self._update_height)
        self._update_height()

    def _update_height(self):
        rows = max(1, self.document().blockCount())
        line_h = self.fontMetrics().lineSpacing()
        pad = dm.SPACE_SM_PX * 2
        new_h = rows * line_h + pad
        min_one = dm.INPUT_MD_HEIGHT_PX + dm.SPACE_XS_PX * 2
        new_h = max(min_one, min(new_h, 200))
        self.setMinimumHeight(new_h)
        self.setMaximumHeight(new_h)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.returnPressed.emit()
        else:
            super().keyPressEvent(event)


class ChatComposerWidget(QWidget):
    """Composer-Bereich: Eingabefeld + Senden, unten fixiert."""

    send_requested = Signal()

    def __init__(self, icons_path: str = "", parent=None):
        super().__init__(parent)
        self.icons_path = icons_path
        self.init_ui()

    def init_ui(self):
        self.setObjectName("chatComposer")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Wrapper für zentrierten Content
        wrapper = QWidget()
        wrapper.setObjectName("composerWrapper")
        wrapper_layout = QHBoxLayout(wrapper)
        wl, wt, wr, wb = dm.CHAT_COMPOSER_WRAPPER_MARGINS_LTRB
        wrapper_layout.setContentsMargins(wl, wt, wr, wb)
        wrapper_layout.setSpacing(0)

        # Container mit abgerundeten Ecken
        container = QWidget()
        container.setObjectName("composerContainer")
        container.setMinimumWidth(0)
        container.setMaximumWidth(dm.CHAT_CONTENT_MAX_WIDTH_PX)

        layout = QHBoxLayout(container)
        il, it, ir, ib = dm.CHAT_COMPOSER_INNER_MARGINS_LTRB
        layout.setContentsMargins(il, it, ir, ib)
        layout.setSpacing(dm.FORM_ROW_GAP_PX)

        self.input_edit = ChatInput()
        self.input_edit.setObjectName("chatInput")
        self.input_edit.setPlaceholderText(
            "Nachricht eingeben…  /fast /think /code /overkill"
        )
        if tip := get_tooltip("chatInput"):
            self.input_edit.setToolTip(tip)
        self.input_edit.returnPressed.connect(self._on_send)
        layout.addWidget(self.input_edit, 1)

        self.send_btn = QPushButton()
        self.send_btn.setObjectName("sendButton")
        self.send_btn.setFixedSize(
            dm.CHAT_PRIMARY_SEND_WIDTH_PX, dm.CHAT_PRIMARY_SEND_HEIGHT_PX
        )
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setToolTip(get_tooltip("sendButton") or "Senden")
        self.send_btn.clicked.connect(self._on_send)
        layout.addWidget(
            self.send_btn, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight
        )

        wrapper_layout.addStretch()
        wrapper_layout.addWidget(container)
        wrapper_layout.addStretch()

        # Slash-Hinweis – dezent unter dem Composer
        hint = QLabel("Tipp: /fast, /think, /code für Moduswechsel")
        hint.setObjectName("composerHint")
        hint_layout = QHBoxLayout()
        hint_layout.addStretch()
        hint_layout.addWidget(hint)
        hint_layout.addStretch()
        main_layout.addWidget(wrapper)
        main_layout.addLayout(hint_layout)

        self.set_icons()

    def set_icons(self):
        ic = IconManager.get(IconRegistry.SEND, size=20, state="primary")
        if not ic.isNull():
            self.send_btn.setIcon(ic)
            self.send_btn.setIconSize(QSize(20, 20))
        else:
            self.send_btn.setText("→")

    def _on_send(self):
        self.send_requested.emit()

    def get_text(self) -> str:
        return self.input_edit.toPlainText().strip()

    def clear_input(self):
        self.input_edit.clear()

    def append_text(self, text: str):
        """Fügt Text am Ende des Eingabefelds ein."""
        self.input_edit.setPlainText(
            self.input_edit.toPlainText() + text
        )
