"""
AgentSummaryPanel – Details zum ausgewählten Agenten.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QScrollArea,
)
from app.gui.shared import BasePanel
from app.agents.agent_profile import AgentProfile


def _panel_style() -> str:
    return (
        "background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; "
        "padding: 12px;"
    )


class AgentSummaryPanel(BasePanel):
    """Zeigt Rolle, Modell, Fähigkeiten des ausgewählten Agenten."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentSummaryPanel")
        self.setMinimumHeight(120)
        self._profile: AgentProfile | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        self._title = QLabel("Agent-Details")
        self._title.setStyleSheet("font-weight: 600; font-size: 14px; color: #1f2937;")
        layout.addWidget(self._title)

        self._content = QLabel("Agent auswählen…")
        self._content.setStyleSheet("color: #6b7280; font-size: 12px;")
        self._content.setWordWrap(True)
        layout.addWidget(self._content, 1)

    def set_agent(self, profile: AgentProfile | None) -> None:
        """Setzt den anzuzeigenden Agenten."""
        self._profile = profile
        if not profile:
            self._content.setText("Agent auswählen…")
            return
        lines = [
            f"<b>Rolle:</b> {profile.role or '—'}",
            f"<b>Modell:</b> {profile.assigned_model or 'Standard'}",
            f"<b>Abteilung:</b> {profile.department or '—'}",
        ]
        if profile.short_description:
            lines.append(f"<b>Beschreibung:</b> {profile.short_description}")
        if profile.capabilities:
            lines.append(f"<b>Fähigkeiten:</b> {', '.join(profile.capabilities)}")
        if profile.tools:
            lines.append(f"<b>Tools:</b> {', '.join(profile.tools)}")
        self._content.setText("<br>".join(lines))
