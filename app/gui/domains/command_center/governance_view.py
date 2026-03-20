"""
GovernanceView – Darstellung der Freeze-Zonen / Governance-Bereiche.

Orientierung: stabiler QA-Kern, aktive Entwicklung, experimentell.
Keine Berechtigungslogik.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QLabel,
    QPushButton,
    QGroupBox,
)
from PySide6.QtCore import Signal

from app.qa.dashboard_adapter import QADashboardAdapter
from app.qa.drilldown_models import GovernanceData
from app.resources.styles import get_theme_colors


class GovernanceView(QWidget):
    """Governance-/Freeze-Zonen-Übersicht."""

    back_requested = Signal()

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.adapter = QADashboardAdapter()
        self.data: GovernanceData | None = None
        self._init_ui()
        self._apply_theme()
        self.refresh()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        back_btn = QPushButton("← Zurück")
        back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(back_btn)
        header.addStretch()
        title = QLabel("Governance / Freeze-Zonen")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        intro = QLabel(
            "Diese Darstellung dient der Orientierung, nicht der Berechtigung. "
            "Trennung zwischen stabilem QA-Kern, aktiver Produktentwicklung und experimentellen Bereichen."
        )
        intro.setWordWrap(True)
        content_layout.addWidget(intro)

        self.zones_layout = QVBoxLayout()
        content_layout.addLayout(self.zones_layout)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def refresh(self):
        self.data = self.adapter.load_governance()
        self._update_ui()

    def _update_ui(self):
        while self.zones_layout.count():
            item = self.zones_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.data or not self.data.zones:
            lbl = QLabel("Keine Governance-Daten.")
            self.zones_layout.addWidget(lbl)
            return

        zone_colors = {"stable": "#10b981", "active": "#4a90d9", "experimental": "#f59e0b"}
        for z in self.data.zones:
            frame = QFrame()
            frame.setObjectName("governanceZone")
            frame.setStyleSheet(f"""
                QFrame#governanceZone {{
                    background-color: #2a2a2a;
                    border-left: 4px solid {zone_colors.get(z.zone_type, '#505050')};
                    border-radius: 8px;
                    padding: 12px;
                    margin: 8px 0;
                }}
            """)
            zone_layout = QVBoxLayout(frame)
            zone_layout.addWidget(QLabel(f"<b>{z.label}</b>"))
            zone_layout.addWidget(QLabel(z.description))
            self.zones_layout.addWidget(frame)

    def _apply_theme(self):
        colors = get_theme_colors(self.theme)
        bg = "#2a2a2a" if self.theme == "dark" else "#f8f8f8"
        for f in self.findChildren(QFrame, "governanceZone"):
            f.setStyleSheet(f"""
                QFrame#governanceZone {{
                    background-color: {bg};
                    border-radius: 8px;
                    padding: 12px;
                    margin: 8px 0;
                }}
            """)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self._apply_theme()
