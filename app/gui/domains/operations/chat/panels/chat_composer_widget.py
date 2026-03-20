"""
ChatComposerWidget – Moderner Composer-Bereich unten.
Großes Eingabefeld, Senden-Button, Slash-Command-Hinweis.
"""

import os

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QLabel,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from app.help.tooltip_helper import get_tooltip


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
        new_h = rows * line_h + 20
        new_h = max(52, min(new_h, 200))
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
        wrapper_layout.setContentsMargins(24, 16, 24, 24)
        wrapper_layout.setSpacing(0)

        # Container mit abgerundeten Ecken
        container = QWidget()
        container.setObjectName("composerContainer")
        container.setMinimumWidth(1000)
        container.setMaximumWidth(1000)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(16, 12, 12, 12)
        layout.setSpacing(12)

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
        self.send_btn.setFixedSize(44, 44)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setToolTip(get_tooltip("sendButton") or "Senden")
        self.send_btn.clicked.connect(self._on_send)
        layout.addWidget(self.send_btn, 0, Qt.AlignBottom)

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
        if self.icons_path:
            path = os.path.join(self.icons_path, "send.svg")
            if os.path.exists(path):
                self.send_btn.setIcon(QIcon(path))
                self.send_btn.setIconSize(QSize(20, 20))
            else:
                self.send_btn.setText("→")
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
