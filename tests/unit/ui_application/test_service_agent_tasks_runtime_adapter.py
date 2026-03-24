"""ServiceAgentTasksRuntimeAdapter (Batch 6)."""

from __future__ import annotations

from app.agents.agent_task_runner import AgentTaskResult
from app.ui_application.adapters.service_agent_tasks_runtime_adapter import ServiceAgentTasksRuntimeAdapter
from app.ui_contracts.workspaces.agent_tasks_runtime import StartAgentTaskCommand


async def test_adapter_maps_result(monkeypatch) -> None:
    r = AgentTaskResult(
        task_id="tid",
        agent_id="aid",
        agent_name="Bob",
        prompt="p",
        response="ok",
        model="llama",
        success=True,
        duration_sec=2.0,
    )

    class _S:
        async def start_agent_task(self, agent_id: str, prompt: str):  # noqa: ANN001
            assert agent_id == "aid"
            assert prompt == "p"
            return r

    monkeypatch.setattr(
        "app.services.agent_service.get_agent_service",
        lambda: _S(),
    )
    ad = ServiceAgentTasksRuntimeAdapter()
    dto = await ad.start_agent_task_runtime(StartAgentTaskCommand("aid", "p"))
    assert dto.task_id == "tid"
    assert dto.agent_name == "Bob"
    assert dto.success is True
    assert dto.duration_sec == 2.0
