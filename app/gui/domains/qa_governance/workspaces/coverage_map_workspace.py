"""
CoverageMapWorkspace – Coverage Overview, Failure Classes, Guards, Regression.
Nutzt QAGovernanceService für reale Daten.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.gui.domains.qa_governance.workspaces.base_analysis_workspace import BaseAnalysisWorkspace
from app.gui.domains.qa_governance.panels.coverage_map_panels import (
    CoverageOverviewPanel,
    CoverageListPanel,
    CoverageDetailPanel,
)


class CoverageMapWorkspace(BaseAnalysisWorkspace):
    """Workspace für Coverage Map."""

    def __init__(self, parent=None):
        super().__init__("qa_coverage_map", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(CoverageOverviewPanel(self))

        self._list_panel = CoverageListPanel(self)
        self._list_panel.entry_selected.connect(self._on_entry_selected)
        content_layout.addWidget(self._list_panel)

        self._detail_panel = CoverageDetailPanel(self)
        content_layout.addWidget(self._detail_panel)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def _on_entry_selected(self, entry):
        self._detail_panel.set_entry(entry)
        if self._inspector_host:
            from app.gui.inspector.coverage_inspector import CoverageInspector
            content = CoverageInspector(
                failure_class=entry.key if entry.axis == "failure_class" else "—",
                guard=entry.key if entry.axis == "guard" else "—",
                coverage_status=f"{entry.strength} · {entry.test_count} Tests",
            )
            self._inspector_host.set_content(content)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Coverage-spezifischen Inspector. D9: content_token optional."""
        super().setup_inspector(inspector_host, content_token=content_token)
        from app.gui.inspector.coverage_inspector import CoverageInspector
        content = CoverageInspector(
            failure_class="(keine)",
            guard="—",
            coverage_status="—",
        )
        inspector_host.set_content(content, content_token=content_token)
