"""
ActivityDetailPanel – Details einer ausgewählten Aktivität.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QTextEdit,
)
from app.debug.agent_event import AgentEvent, EventType


def _panel_style() -> str:
    return (
        "background: #0f172a; border: 1px solid #334155; border-radius: 8px; "
        "padding: 12px;"
    )


class ActivityDetailPanel(QFrame):
    """Zeigt Details einer ausgewählten Aktivität: Prompt, Modell, Ergebnis."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("activityDetailPanel")
        self.setMinimumHeight(120)
        self._event: AgentEvent | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Aktivitätsdetails")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #94a3b8;")
        layout.addWidget(title)

        self._content = QTextEdit()
        self._content.setReadOnly(True)
        self._content.setPlaceholderText("Aktivität auswählen…")
        self._content.setStyleSheet(
            "QTextEdit { background: #1e293b; color: #cbd5e1; border: none; "
            "border-radius: 6px; padding: 8px; font-size: 12px; }"
        )
        layout.addWidget(self._content, 1)

    def set_event(self, event: AgentEvent | None) -> None:
        """Setzt die anzuzeigende Aktivität."""
        self._event = event
        if not event:
            self._content.clear()
            self._content.setPlaceholderText("Aktivität auswählen…")
            return
        lines = [
            f"Agent: {event.agent_name}",
            f"Typ: {event.event_type.value if hasattr(event.event_type, 'value') else event.event_type}",
            f"Zeit: {event.timestamp.strftime('%H:%M:%S') if event.timestamp else '—'}",
            f"Nachricht: {event.message or '—'}",
        ]
        if event.metadata:
            for k, v in event.metadata.items():
                if v is not None:
                    lines.append(f"{k}: {v}")
        self._content.setPlainText("\n".join(lines))
