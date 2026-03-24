"""ServiceAgentTasksRegistryAdapter."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.qa.operations_models import AgentOperationsIssue, AgentOperationsSummary


@dataclass
class _Summary:
    agent_id: str
    issues: list = field(default_factory=list)


@dataclass
class _Prof:
    id: str | None
    name: str = "N"
    display_name: str = ""
    role: str = ""
    status: str = "active"
    assigned_model: str | None = None

    @property
    def effective_display_name(self) -> str:
        return self.display_name or self.name


class _AgentSvc:
    def __init__(self, agents: list) -> None:
        self._agents = agents

    def list_agents_for_project(self, project_id, department=None, status=None, filter_text=""):  # noqa: ANN001
        del project_id, department, status, filter_text
        return list(self._agents)


class _ReadSvc:
    def __init__(self, summaries: list, get_summary_result=None) -> None:
        self._s = summaries
        self._gs = get_summary_result
        self.get_summary_calls = 0

    def list_summaries(self, project_id):  # noqa: ANN001
        del project_id
        return list(self._s)

    def get_summary(self, agent_id, project_id):  # noqa: ANN001
        del project_id
        self.get_summary_calls += 1
        return self._gs


def test_adapter_no_project() -> None:
    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    ad = ServiceAgentTasksRegistryAdapter()
    v = ad.load_registry_view(None)
    assert v.phase == "no_project"
    assert ad.last_registry_snapshot is None


def test_adapter_happy(monkeypatch) -> None:
    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    p = _Prof(id="a1", display_name="Agent One", role="r")
    monkeypatch.setattr(
        "app.services.agent_service.get_agent_service",
        lambda: _AgentSvc([p]),
    )
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.get_agent_operations_read_service",
        lambda: _ReadSvc([_Summary("a1", issues=[1, 2])], get_summary_result=None),
    )
    ad = ServiceAgentTasksRegistryAdapter()
    v = ad.load_registry_view(5)
    assert v.phase == "ready"
    assert len(v.rows) == 1
    assert "Hinweis" in v.rows[0].list_item_text
    snap = ad.last_registry_snapshot
    assert snap is not None
    assert snap.agents == [p]
    assert snap.profiles_by_id["a1"] is p
    assert "a1" in snap.summaries_by_id


def test_adapter_empty(monkeypatch) -> None:
    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    monkeypatch.setattr(
        "app.services.agent_service.get_agent_service",
        lambda: _AgentSvc([]),
    )
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.get_agent_operations_read_service",
        lambda: _ReadSvc([], get_summary_result=None),
    )
    ad = ServiceAgentTasksRegistryAdapter()
    v = ad.load_registry_view(1)
    assert v.phase == "empty"
    snap = ad.last_registry_snapshot
    assert snap is not None
    assert snap.agents == []
    assert snap.summaries_by_id == {}


def test_adapter_list_error(monkeypatch) -> None:
    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    def _boom():
        raise RuntimeError("x")

    monkeypatch.setattr(
        "app.services.agent_service.get_agent_service",
        _boom,
    )
    ad = ServiceAgentTasksRegistryAdapter()
    v = ad.load_registry_view(1)
    assert v.phase == "error"
    assert ad.last_registry_snapshot is None


def _full_summary(aid: str) -> AgentOperationsSummary:
    return AgentOperationsSummary(
        agent_id=aid,
        slug="s",
        display_name="D",
        status="active",
        assigned_model="m",
        model_role="r",
        cloud_allowed=False,
        last_activity_at=None,
        last_activity_source="none",
        issues=[AgentOperationsIssue("C", "warning", "msg")],
        workflow_definition_ids=["w1"],
    )


def test_adapter_registry_snapshot_holds_agent_operations_summaries(monkeypatch) -> None:
    """Slice 2b: Snapshot enthält echte Summaries (AgentOperationsSummary) für Selection-Cache."""
    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    p = _Prof(id="a1", display_name="Agent One", role="r")
    summ = _full_summary("a1")
    monkeypatch.setattr(
        "app.services.agent_service.get_agent_service",
        lambda: _AgentSvc([p]),
    )
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.get_agent_operations_read_service",
        lambda: _ReadSvc([summ], get_summary_result=None),
    )
    ad = ServiceAgentTasksRegistryAdapter()
    ad.load_registry_view(3)
    snap = ad.last_registry_snapshot
    assert snap is not None
    assert snap.summaries_by_id["a1"] is summ


def test_adapter_selection_cache_hit_skips_get_summary(monkeypatch) -> None:
    from app.ui_contracts.workspaces.agent_tasks_registry import LoadAgentTaskSelectionCommand

    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    p = _Prof(id="a1", display_name="Agent One", role="r")
    summ = _full_summary("a1")
    read = _ReadSvc([summ], get_summary_result=None)
    monkeypatch.setattr(
        "app.services.agent_service.get_agent_service",
        lambda: _AgentSvc([p]),
    )
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.get_agent_operations_read_service",
        lambda: read,
    )
    ad = ServiceAgentTasksRegistryAdapter()
    ad.load_registry_view(5)
    st = ad.load_agent_task_selection_detail(LoadAgentTaskSelectionCommand("a1", 5))
    assert st.phase == "ready"
    assert st.summary is not None
    assert st.summary.agent_id == "a1"
    assert read.get_summary_calls == 0


def test_adapter_selection_get_summary_on_cache_miss(monkeypatch) -> None:
    from app.ui_contracts.workspaces.agent_tasks_registry import LoadAgentTaskSelectionCommand

    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    p = _Prof(id="a1", display_name="Agent One", role="r")
    fetched = _full_summary("a1")
    # list_summaries leer → kein Cache-Treffer, Selection muss get_summary nutzen
    read = _ReadSvc([], get_summary_result=fetched)
    monkeypatch.setattr(
        "app.services.agent_service.get_agent_service",
        lambda: _AgentSvc([p]),
    )
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.get_agent_operations_read_service",
        lambda: read,
    )
    ad = ServiceAgentTasksRegistryAdapter()
    ad.load_registry_view(5)
    st = ad.load_agent_task_selection_detail(LoadAgentTaskSelectionCommand("a1", 5))
    assert st.phase == "ready"
    assert st.summary is not None
    assert read.get_summary_calls == 1


def test_adapter_selection_idle_empty_agent_id() -> None:
    from app.ui_contracts.workspaces.agent_tasks_registry import LoadAgentTaskSelectionCommand

    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    st = ServiceAgentTasksRegistryAdapter().load_agent_task_selection_detail(
        LoadAgentTaskSelectionCommand("  ", 1),
    )
    assert st.phase == "idle"


def test_adapter_selection_error_on_get_summary(monkeypatch) -> None:
    from app.ui_contracts.workspaces.agent_tasks_registry import LoadAgentTaskSelectionCommand

    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    class _BoomRead:
        get_summary_calls = 0

        def get_summary(self, *a, **k):  # noqa: ANN002
            self.get_summary_calls += 1
            raise RuntimeError("boom")

    boom = _BoomRead()
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.get_agent_operations_read_service",
        lambda: boom,
    )
    st = ServiceAgentTasksRegistryAdapter().load_agent_task_selection_detail(
        LoadAgentTaskSelectionCommand("a1", 1),
    )
    assert st.phase == "error"
    assert st.error is not None


def test_adapter_inspector_read_empty_agent_id() -> None:
    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    d = ServiceAgentTasksRegistryAdapter().load_agent_tasks_inspector_state("  ", 1)
    assert d.load_error is None
    assert d.operations_agent_status == ""


def test_adapter_inspector_read_no_project() -> None:
    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    d = ServiceAgentTasksRegistryAdapter().load_agent_tasks_inspector_state("a1", None)
    assert d.load_error is None
    assert "Projekt" in d.operations_task_context


def test_adapter_inspector_read_cache_hit(monkeypatch) -> None:
    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    p = _Prof(id="a1", display_name="Agent One", role="r")
    summ = _full_summary("a1")
    read = _ReadSvc([summ], get_summary_result=None)
    monkeypatch.setattr(
        "app.services.agent_service.get_agent_service",
        lambda: _AgentSvc([p]),
    )
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.get_agent_operations_read_service",
        lambda: read,
    )
    ad = ServiceAgentTasksRegistryAdapter()
    ad.load_registry_view(5)
    d = ad.load_agent_tasks_inspector_state("a1", 5)
    assert d.load_error is None
    assert "Betrieb" in d.operations_agent_status
    assert read.get_summary_calls == 0


def test_adapter_selection_no_project_no_get_summary(monkeypatch) -> None:
    from app.ui_contracts.workspaces.agent_tasks_registry import LoadAgentTaskSelectionCommand

    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter

    read = _ReadSvc([], get_summary_result=_full_summary("a1"))

    def _no():
        raise AssertionError("get_agent_service should not run")

    monkeypatch.setattr("app.services.agent_service.get_agent_service", _no)
    monkeypatch.setattr(
        "app.services.agent_operations_read_service.get_agent_operations_read_service",
        lambda: read,
    )
    st = ServiceAgentTasksRegistryAdapter().load_agent_task_selection_detail(
        LoadAgentTaskSelectionCommand("a1", None),
    )
    assert st.phase == "ready"
    assert st.summary is None
    assert read.get_summary_calls == 0
