"""
TestInventoryWorkspace – Test List, Kategorien, Status, Details, Filter.
Nutzt QAGovernanceService für reale Daten.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.gui.domains.qa_governance.workspaces.base_analysis_workspace import BaseAnalysisWorkspace
from app.gui.domains.qa_governance.panels.test_inventory_panels import (
    TestListPanel,
    TestSummaryPanel,
    TestDetailPanel,
)


class TestInventoryWorkspace(BaseAnalysisWorkspace):
    """Workspace für Test Inventory."""

    def __init__(self, parent=None):
        super().__init__("qa_test_inventory", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self._list_panel = TestListPanel(self)
        self._list_panel.test_selected.connect(self._on_test_selected)
        content_layout.addWidget(self._list_panel)

        content_layout.addWidget(TestSummaryPanel(self))

        self._detail_panel = TestDetailPanel(self)
        content_layout.addWidget(self._detail_panel)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def _on_test_selected(self, test):
        self._detail_panel.set_test(test)
        if self._inspector_host:
            from app.gui.inspector.test_inspector import TestInspector
            content = TestInspector(
                test_id=test.id[:50] + "…" if len(test.id) > 50 else test.id,
                category=test.test_type,
                status="—",
                tags=f"{test.subsystem}, {test.test_domain}",
                mapping=", ".join(test.failure_classes[:2]) or "—",
            )
            self._inspector_host.set_content(content)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Test-spezifischen Inspector. D9: content_token optional."""
        super().setup_inspector(inspector_host, content_token=content_token)
        from app.gui.inspector.test_inspector import TestInspector
        content = TestInspector(
            test_id="(keine)",
            category="—",
            status="—",
            tags="—",
            mapping="—",
        )
        inspector_host.set_content(content, content_token=content_token)
