"""
QA Dashboard – Read-only Adapter für die Kommandozentrale.

Keine Änderung an scripts/qa oder docs/qa.
Liest ausschließlich vorhandene Artefakte.
"""

from app.qa.dashboard_adapter import QADashboardAdapter, DashboardData
from app.qa.drilldown_models import (
    QADrilldownData,
    SubsystemDetailData,
    GovernanceData,
)
from app.qa.operations_adapter import OperationsAdapter
from app.qa.operations_models import (
    IncidentOperationsData,
    QAOperationsData,
    ReviewOperationsData,
    AuditOperationsData,
)

__all__ = [
    "QADashboardAdapter",
    "DashboardData",
    "QADrilldownData",
    "SubsystemDetailData",
    "GovernanceData",
    "OperationsAdapter",
    "IncidentOperationsData",
    "QAOperationsData",
    "ReviewOperationsData",
    "AuditOperationsData",
]
