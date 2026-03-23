"""
IncidentsPanel – Kurzüberblick aus QA-Gap-Daten (read-only).
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class IncidentsPanel(BasePanel):
    """Panel: Gap-/Incident-Hinweise aus QA-JSON."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self._detail: QLabel | None = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("Incidents / Gaps")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        self._detail = QLabel("")
        self._detail.setObjectName("panelMeta")
        self._detail.setWordWrap(True)
        layout.addWidget(self._detail)

        layout.addStretch()

    def refresh(self) -> None:
        if not self._detail:
            return
        try:
            from app.qa.dashboard_adapter import QADashboardAdapter

            data = QADashboardAdapter().load()
            ex = data.executive
            orphans = ex.orphan_backlog
            self._detail.setText(
                f"Orphan-Backlog (Inventory): {orphans} · "
                f"priorisierte Gaps: {ex.prioritized_gaps}. "
                "Detail: Kommandozentrale → QA Drilldown oder docs/qa/."
            )
        except Exception as e:
            self._detail.setText(f"Konnte Gap-Daten nicht lesen: {e}")
