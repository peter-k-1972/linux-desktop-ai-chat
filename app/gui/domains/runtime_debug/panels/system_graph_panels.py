"""
System Graph Panels – Systemübersicht, Komponenten, strukturierte Darstellung.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QGridLayout,
)
from app.gui.domains.runtime_debug.rd_surface_styles import (
    rd_panel_qss,
    rd_section_title_qss,
    rd_body_secondary_qss,
    rd_node_card_qss,
    rd_card_title_qss,
    rd_card_status_qss,
    rd_graph_ok_border_color,
)


def _node_card(name: str, status: str, border_color: str) -> QFrame:
    """Erstellt eine Komponenten-Karte für den System-Graphen."""
    card = QFrame()
    card.setStyleSheet(rd_node_card_qss(border_color=border_color))
    layout = QVBoxLayout(card)
    layout.setContentsMargins(12, 12, 12, 12)
    n = QLabel(name)
    n.setStyleSheet(rd_card_title_qss())
    layout.addWidget(n)
    s = QLabel(status)
    s.setStyleSheet(rd_card_status_qss(border_color))
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
        self.setStyleSheet(rd_panel_qss())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("System Graph")
        title.setStyleSheet(rd_section_title_qss())
        layout.addWidget(title)

        subtitle = QLabel("Komponenten: Chat · Agents · Models · Tools · Datastores")
        subtitle.setStyleSheet(rd_body_secondary_qss())
        layout.addWidget(subtitle)

        ok = rd_graph_ok_border_color()
        grid = QGridLayout()
        grid.addWidget(_node_card("Chat", "Active", ok), 0, 0)
        grid.addWidget(_node_card("Agents", "2 Active", ok), 0, 1)
        grid.addWidget(_node_card("Models", "Ollama", ok), 0, 2)
        grid.addWidget(_node_card("Tools", "7 Available", ok), 1, 0)
        grid.addWidget(_node_card("Datastores", "Connected", ok), 1, 1)
        grid.addWidget(_node_card("EventBus", "Running", ok), 1, 2)
        layout.addLayout(grid)
