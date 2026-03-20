"""
UI Tests: AgentPerformanceTab – Metrics in Profil.

P2: Metrics -> Profil-Timeline zeigt Daten.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.metrics.agent_metrics import AgentMetric, AgentStatistics, TimeRange
from app.gui.domains.control_center.agents_ui.agent_performance_tab import AgentPerformanceTab


class FakeMetricsService:
    """Fake MetricsService mit Testdaten."""

    def get_agent_statistics(self, agent_id, time_range=TimeRange.ALL):
        return AgentStatistics(
            agent_id=agent_id,
            total_tasks=5,
            tasks_completed=4,
            tasks_failed=1,
            success_rate=0.8,
            avg_runtime=2.5,
            most_used_model="test-model",
            model_usage_distribution={"test-model": 4},
        )

    def get_metrics_range(self, agent_id, time_range=TimeRange.ALL, bucket_hours=1):
        return [
            AgentMetric(
                timestamp=datetime.now(timezone.utc),
                agent_id=agent_id,
                tasks_completed=2,
                tasks_failed=0,
                avg_runtime=2.0,
            ),
        ]


@pytest.mark.ui
def test_metrics_timeline_in_agent_profile(qtbot):
    """
    Metrics -> Profil-Timeline zeigt Daten.
    Verhindert: Performance-Tab zeigt keine Metrikdaten.
    """
    service = FakeMetricsService()
    profile = AgentProfile(
        id="p2-metrics-agent",
        name="P2-Metrics-Test",
        display_name="Metrics Test",
        slug="p2_metrics",
        department="research",
        status=AgentStatus.ACTIVE.value,
    )

    tab = AgentPerformanceTab(theme="dark", metrics_service=service)
    qtbot.addWidget(tab)
    tab.load_profile(profile)
    qtbot.wait(100)

    assert tab.stat_labels["total_tasks"].text() == "5"
    assert "80" in tab.stat_labels["success_rate"].text()
    assert "2.5" in tab.stat_labels["avg_runtime"].text()
    assert tab.stat_labels["most_model"].text() == "test-model"
