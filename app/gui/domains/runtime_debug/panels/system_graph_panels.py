"""
System Graph Panels – Systemübersicht, Komponenten, strukturierte Darstellung.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
)
from PySide6.QtCore import Qt


def _rd_panel_style() -> str:
    return (
        "background: #0f172a; border: 1px solid #334155; border-radius: 8px; "
        "padding: 12px;"
    )


def _node_card(name: str, status: str, color: str = "#34d399") -> QFrame:
    """Erstellt eine Komponenten-Karte für den System-Graphen."""
    card = QFrame()
    card.setStyleSheet(
        f"background: #1e293b; border: 1px solid {color}; border-radius: 8px; "
        "padding: 12px;"
    )
    layout = QVBoxLayout(card)
    layout.setContentsMargins(12, 12, 12, 12)
    n = QLabel(name)
    n.setStyleSheet("color: #cbd5e1; font-weight: 600; font-size: 12px;")
    layout.addWidget(n)
    s = QLabel(status)
    s.setStyleSheet(f"color: {color}; font-size: 11px;")
    layout.addWidget(s)
    return card


class SystemGraphPanel(QFrame):
    """Systemübersicht – Chat, Agents, Models, Tools, Datastores."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("systemGraphPanel")
        self.setMinimumHeight(280)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_rd_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("System Graph")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #94a3b8;")
        layout.addWidget(title)

        subtitle = QLabel("Komponenten: Chat · Agents · Models · Tools · Datastores")
        subtitle.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(subtitle)

        grid = QGridLayout()
        grid.addWidget(_node_card("Chat", "Active", "#34d399"), 0, 0)
        grid.addWidget(_node_card("Agents", "2 Active", "#34d399"), 0, 1)
        grid.addWidget(_node_card("Models", "Ollama", "#34d399"), 0, 2)
        grid.addWidget(_node_card("Tools", "7 Available", "#34d399"), 1, 0)
        grid.addWidget(_node_card("Datastores", "Connected", "#34d399"), 1, 1)
        grid.addWidget(_node_card("EventBus", "Running", "#34d399"), 1, 2)
        layout.addLayout(grid)
