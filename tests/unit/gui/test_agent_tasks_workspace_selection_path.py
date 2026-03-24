"""AgentTasksWorkspace — Selection-/Detail-Pfad Slice 2."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.agents.agent_profile import AgentProfile


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _qapp()
    yield


def test_on_agent_selected_port_path_calls_selection_presenter(qapp) -> None:
    from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import AgentTasksWorkspace

    calls = []
    ws = AgentTasksWorkspace()
    ws._selection_presenter.handle_command = lambda c: calls.append(c)  # type: ignore[method-assign]
    prof = AgentProfile(id="p1", name="P")
    ws._last_project_id = 2
    ws._on_agent_selected(prof)
    assert len(calls) == 1
    assert calls[0].agent_id == "p1"
    assert calls[0].project_id == 2


def test_on_agent_selected_clears_detail_via_idle_command(qapp) -> None:
    from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import AgentTasksWorkspace

    calls = []
    ws = AgentTasksWorkspace()
    ws._selection_presenter.handle_command = lambda c: calls.append(c)  # type: ignore[method-assign]
    ws._on_agent_selected(None)
    assert len(calls) == 1
    assert calls[0].agent_id == ""


def test_selection_presenter_used_even_when_registry_not_port_driven(qapp, monkeypatch) -> None:
    """Batch 5: Operations-Summary-Read läuft über Presenter/Adapter, nicht über Registry-Port-Flag."""
    from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import AgentTasksWorkspace

    calls = []
    ws = AgentTasksWorkspace()
    ws._selection_presenter.handle_command = lambda c: calls.append(c)  # type: ignore[method-assign]
    monkeypatch.setattr(ws._registry, "uses_port_driven_registry", lambda: False)
    prof = AgentProfile(id="z1", name="Z")
    ws._last_project_id = 5
    ws._on_agent_selected(prof)
    assert len(calls) == 1
    assert calls[0].agent_id == "z1"
    assert calls[0].project_id == 5


def test_legacy_path_calls_get_summary_when_cache_empty(qapp, monkeypatch) -> None:
    from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import AgentTasksWorkspace
    from app.ui_application.adapters.service_agent_tasks_registry_adapter import AgentTasksRegistrySnapshot

    args: list[tuple[str, int]] = []

    class _R:
        def get_summary(self, agent_id: str, project_id: int):
            args.append((agent_id, project_id))
            return None

    monkeypatch.setattr(
        "app.services.agent_operations_read_service.get_agent_operations_read_service",
        lambda: _R(),
    )
    ws = AgentTasksWorkspace()
    monkeypatch.setattr(ws._registry, "uses_port_driven_registry", lambda: False)
    ws._registry_adapter.last_registry_snapshot = AgentTasksRegistrySnapshot(
        agents=[],
        profiles_by_id={},
        summaries_by_id={},
    )
    ws._last_project_id = 9
    ws._on_agent_selected(AgentProfile(id="ax", name="N"))
    assert args == [("ax", 9)]
