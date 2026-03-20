"""QA & Governance Panels."""

from app.gui.domains.qa_governance.panels.test_inventory_panels import (
    TestListPanel,
    TestSummaryPanel,
    TestDetailPanel,
)
from app.gui.domains.qa_governance.panels.coverage_map_panels import (
    CoverageOverviewPanel,
    CoverageListPanel,
    CoverageDetailPanel,
)
from app.gui.domains.qa_governance.panels.gap_analysis_panels import (
    GapListPanel,
    GapSummaryPanel,
    GapDetailPanel,
)
from app.gui.domains.qa_governance.panels.incidents_panels import (
    IncidentListPanel,
    IncidentSummaryPanel,
    IncidentDetailPanel,
)
from app.gui.domains.qa_governance.panels.replay_lab_panels import (
    ReplayListPanel,
    ReplaySummaryPanel,
    ReplayDetailPanel,
)

__all__ = [
    "TestListPanel",
    "TestSummaryPanel",
    "TestDetailPanel",
    "CoverageOverviewPanel",
    "CoverageListPanel",
    "CoverageDetailPanel",
    "GapListPanel",
    "GapSummaryPanel",
    "GapDetailPanel",
    "IncidentListPanel",
    "IncidentSummaryPanel",
    "IncidentDetailPanel",
    "ReplayListPanel",
    "ReplaySummaryPanel",
    "ReplayDetailPanel",
]
