"""R2: Agent Operations Read Service."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.agents.agent_profile import AgentProfile
from app.metrics.agent_metrics import AgentMetricEvent, MetricEventType
from app.metrics.metrics_store import MetricsStore
from app.services.agent_operations_read_service import (
    AgentOperationsReadService,
    reset_agent_operations_read_service,
)
from app.workflows.models.definition import WorkflowDefinition, WorkflowNode


@pytest.fixture(autouse=True)
def _reset_read_singleton():
    reset_agent_operations_read_service()
    yield
    reset_agent_operations_read_service()


def test_last_activity_none_without_metrics(tmp_path, monkeypatch):
    db_path = str(tmp_path / "m.db")
    store = MetricsStore(db_path)
    p = AgentProfile(
        id="a1",
        slug="p1",
        name="N",
        display_name="N",
        status="active",
        assigned_model="llama:latest",
    )
    mock_agent = MagicMock()
    mock_agent.list_agents_for_project.return_value = [p]
    monkeypatch.setattr("app.services.agent_service.get_agent_service", lambda: mock_agent)
    wf = MagicMock()
    wf.list_workflows.return_value = []
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.fetch_ollama_tag_names",
        lambda base_url=None: (["llama:latest"], "http://x"),
    )
    svc = AgentOperationsReadService(metrics_store=store, workflow_service_getter=lambda: wf)
    rows = svc.list_summaries(1)
    assert len(rows) == 1
    assert rows[0].last_activity_at is None
    assert rows[0].last_activity_source == "none"


def test_last_activity_from_metrics(tmp_path, monkeypatch):
    db_path = str(tmp_path / "m2.db")
    store = MetricsStore(db_path)
    ts = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    store.insert_event(
        AgentMetricEvent(
            timestamp=ts,
            agent_id="a1",
            event_type=MetricEventType.TASK_COMPLETED,
            task_id="t",
            duration_sec=1.0,
        )
    )
    p = AgentProfile(
        id="a1",
        slug="p1",
        name="N",
        display_name="N",
        status="active",
        assigned_model="llama:latest",
    )
    mock_agent = MagicMock()
    mock_agent.list_agents_for_project.return_value = [p]
    monkeypatch.setattr("app.services.agent_service.get_agent_service", lambda: mock_agent)
    wf = MagicMock()
    wf.list_workflows.return_value = []
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.fetch_ollama_tag_names",
        lambda base_url=None: (["llama:latest"], "http://x"),
    )
    svc = AgentOperationsReadService(metrics_store=store, workflow_service_getter=lambda: wf)
    rows = svc.list_summaries(1)
    assert rows[0].last_activity_source == "metrics"
    assert rows[0].last_activity_at


def test_issue_inactive_and_no_model(monkeypatch, tmp_path):
    db_path = str(tmp_path / "m3.db")
    store = MetricsStore(db_path)
    p = AgentProfile(
        id="a1",
        slug="p1",
        name="N",
        display_name="N",
        status="inactive",
        assigned_model="",
    )
    mock_agent = MagicMock()
    mock_agent.list_agents_for_project.return_value = [p]
    monkeypatch.setattr("app.services.agent_service.get_agent_service", lambda: mock_agent)
    wf = MagicMock()
    wf.list_workflows.return_value = []
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.fetch_ollama_tag_names",
        lambda base_url=None: (None, "offline"),
    )
    svc = AgentOperationsReadService(metrics_store=store, workflow_service_getter=lambda: wf)
    rows = svc.list_summaries(1)
    codes = {i.code for i in rows[0].issues}
    assert "AGENT_INACTIVE" in codes
    assert "NO_ASSIGNED_MODEL" in codes
    assert "MODEL_NOT_IN_OLLAMA_TAGS" not in codes


def test_issue_model_not_in_tags_when_ollama_lists(monkeypatch, tmp_path):
    db_path = str(tmp_path / "m4.db")
    store = MetricsStore(db_path)
    p = AgentProfile(
        id="a1",
        slug="p1",
        name="N",
        display_name="N",
        status="active",
        assigned_model="missing:latest",
    )
    mock_agent = MagicMock()
    mock_agent.list_agents_for_project.return_value = [p]
    monkeypatch.setattr("app.services.agent_service.get_agent_service", lambda: mock_agent)
    wf = MagicMock()
    wf.list_workflows.return_value = []
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.fetch_ollama_tag_names",
        lambda base_url=None: (["other:latest"], "http://x"),
    )
    svc = AgentOperationsReadService(metrics_store=store, workflow_service_getter=lambda: wf)
    rows = svc.list_summaries(1)
    assert any(i.code == "MODEL_NOT_IN_OLLAMA_TAGS" for i in rows[0].issues)


def test_workflow_definition_ids_for_agent(monkeypatch, tmp_path):
    db_path = str(tmp_path / "m5.db")
    store = MetricsStore(db_path)
    p = AgentProfile(
        id="aid",
        slug="sluggy",
        name="N",
        display_name="N",
        status="active",
        assigned_model="x",
    )
    mock_agent = MagicMock()
    mock_agent.list_agents_for_project.return_value = [p]
    monkeypatch.setattr("app.services.agent_service.get_agent_service", lambda: mock_agent)
    node = WorkflowNode(
        node_id="n1",
        node_type="agent",
        config={"agent_slug": "sluggy"},
    )
    d = WorkflowDefinition(workflow_id="w99", name="W", nodes=[node], edges=[])
    wf = MagicMock()
    wf.list_workflows.return_value = [d]
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.fetch_ollama_tag_names",
        lambda base_url=None: (["x"], "http://x"),
    )
    svc = AgentOperationsReadService(metrics_store=store, workflow_service_getter=lambda: wf)
    rows = svc.list_summaries(1)
    assert rows[0].workflow_definition_ids == ["w99"]


def test_get_summary_does_not_invoke_list_summaries(monkeypatch, tmp_path):
    db_path = str(tmp_path / "gs.db")
    store = MetricsStore(db_path)
    p = AgentProfile(
        id="a1",
        slug="p1",
        name="N",
        display_name="N",
        status="active",
        assigned_model="llama:latest",
    )
    facade = MagicMock()
    facade.get_agent.return_value = p
    facade.list_agents_for_project.return_value = [p]
    monkeypatch.setattr("app.services.agent_service.get_agent_service", lambda: facade)
    wf = MagicMock()
    wf.list_workflows.return_value = []
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.fetch_ollama_tag_names",
        lambda base_url=None: (["llama:latest"], "http://x"),
    )
    svc = AgentOperationsReadService(metrics_store=store, workflow_service_getter=lambda: wf)

    def _boom(*_a, **_k):
        raise AssertionError("list_summaries must not be called by get_summary")

    svc.list_summaries = _boom  # type: ignore[method-assign]
    out = svc.get_summary("a1", 1)
    assert out is not None
    assert out.agent_id == "a1"
