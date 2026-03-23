"""
AgentResultPanel – Zeigt Ergebnis eines abgeschlossenen Agent-Tasks.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QTextEdit,
)

from app.gui.shared import BasePanel
from app.gui.shared.markdown.markdown_types import RenderTarget
from app.gui.shared.markdown_ui import apply_markdown_to_widget
from app.agents.agent_task_runner import AgentTaskResult


def _panel_style() -> str:
    return (
        "background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; "
        "padding: 12px;"
    )


class AgentResultPanel(BasePanel):
    """Zeigt Prompt, Antwort und Status des letzten Tasks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentResultPanel")
        self.setMinimumHeight(200)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Ergebnis")
        title.setStyleSheet("font-weight: 600; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        self._result = QTextEdit()
        self._result.setReadOnly(True)
        self._result.setPlaceholderText("Task-Ergebnis erscheint hier…")
        self._result.setStyleSheet(
            "QTextEdit { border: 1px solid #e5e7eb; border-radius: 8px; "
            "padding: 8px; font-size: 13px; }"
        )
        layout.addWidget(self._result, 1)

    def set_result(self, result: AgentTaskResult | None) -> None:
        """Setzt das anzuzeigende Ergebnis (Markdown-Pipeline wie Hilfe/Chat)."""
        if not result:
            self._result.clear()
            self._result.setPlaceholderText("Task-Ergebnis erscheint hier…")
            return
        if result.success:
            text = f"[{result.agent_name} · {result.model}]\n\n{result.response or ''}"
        else:
            text = f"[Fehler: {result.agent_name}]\n\n{result.error or 'Unbekannter Fehler'}"
        apply_markdown_to_widget(
            self._result,
            text,
            target=RenderTarget.GENERIC_HTML,
        )
