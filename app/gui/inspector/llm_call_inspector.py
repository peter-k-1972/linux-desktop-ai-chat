"""
LLMCallInspector – Inspector-Inhalt für Prompt / Antwort / Tokens.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class LLMCallInspector(QWidget):
    """Inspector für LLM-Call-Kontext im Runtime-/Debug-Bereich."""

    def __init__(
        self,
        model: str = "—",
        tokens: str = "—",
        duration: str = "—",
        status: str = "—",
        prompt_preview: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("llmCallInspector")
        self._model = model
        self._tokens = tokens
        self._duration = duration
        self._status = status
        self._prompt_preview = prompt_preview
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Model", self._model),
            ("Tokens / Duration", f"{self._tokens} · {self._duration}"),
            ("Status", self._status),
            ("Prompt Preview", self._prompt_preview),
        ]:
            group = QGroupBox(title)
            group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
            gl = QVBoxLayout(group)
            label = QLabel(text)
            label.setStyleSheet("color: #6b7280; font-size: 12px; font-family: monospace;")
            label.setWordWrap(True)
            gl.addWidget(label)
            layout.addWidget(group)

        layout.addStretch()
