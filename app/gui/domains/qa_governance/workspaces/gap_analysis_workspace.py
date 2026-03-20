"""
GapAnalysisWorkspace – Gap Summary, Priorität, Review Candidates.
Nutzt QAGovernanceService für reale Daten.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.gui.domains.qa_governance.workspaces.base_analysis_workspace import BaseAnalysisWorkspace
from app.gui.domains.qa_governance.panels.gap_analysis_panels import (
    GapListPanel,
    GapSummaryPanel,
    GapDetailPanel,
)


class GapAnalysisWorkspace(BaseAnalysisWorkspace):
    """Workspace für Gap Analysis."""

    def __init__(self, parent=None):
        super().__init__("qa_gap_analysis", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(GapSummaryPanel(self))

        self._list_panel = GapListPanel(self)
        self._list_panel.gap_selected.connect(self._on_gap_selected)
        content_layout.addWidget(self._list_panel)

        self._detail_panel = GapDetailPanel(self)
        content_layout.addWidget(self._detail_panel)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def _on_gap_selected(self, gap):
        self._detail_panel.set_gap(gap)
        if self._inspector_host:
            from app.gui.inspector.gap_inspector import GapInspector
            content = GapInspector(
                gap_id=gap.id,
                gap_type=gap.gap_type,
                priority=gap.severity,
                status="—",
                review_hint=gap.title[:80] if gap.title else "—",
            )
            self._inspector_host.set_content(content)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Gap-spezifischen Inspector. D9: content_token optional."""
        super().setup_inspector(inspector_host, content_token=content_token)
        from app.gui.inspector.gap_inspector import GapInspector
        content = GapInspector(
            gap_id="(keine)",
            gap_type="—",
            priority="—",
            status="—",
            review_hint="—",
        )
        inspector_host.set_content(content, content_token=content_token)
