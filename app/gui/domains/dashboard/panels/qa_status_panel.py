"""
QAStatusPanel – Kennzahlen aus docs/qa-Artefakten (QADashboardAdapter).
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class QAStatusPanel(BasePanel):
    """Panel: QA-Inventory / Gap-Report, read-only."""

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

        title = QLabel("QA Status")
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
            self._detail.setText(
                f"Tests (Inventory): {ex.test_count} · "
                f"priorisierte Gaps: {ex.prioritized_gaps} · "
                f"QA-Health: {ex.qa_health} · "
                f"Letzte Verifikation: {ex.last_verification or '—'}"
            )
        except Exception as e:
            self._detail.setText(f"QA-Daten konnten nicht geladen werden: {e}")
