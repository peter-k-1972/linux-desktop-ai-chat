"""PromptPreviewPanel – Live-Vorschau des Editor-Inhalts (nur Lesen)."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTextEdit
from app.gui.shared import BasePanel


class PromptPreviewPanel(BasePanel):
    """Zeigt Titel und Rohtext des Prompts parallel zum Editor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("promptPreviewPanel")
        self.setMinimumHeight(140)
        self._title_lbl: QLabel | None = None
        self._body: QTextEdit | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QLabel("Vorschau")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(header)

        self._title_lbl = QLabel("—")
        self._title_lbl.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._title_lbl)

        self._body = QTextEdit()
        self._body.setReadOnly(True)
        self._body.setPlaceholderText("Kein Inhalt – Prompt wählen oder eingeben.")
        self._body.setStyleSheet("background: #f9fafb; font-size: 12px;")
        layout.addWidget(self._body, 1)

    def on_editor_state(self, title: str, body: str) -> None:
        if self._title_lbl:
            self._title_lbl.setText(f"Titel: {title or '—'}")
        if self._body:
            self._body.setPlainText(body or "")
