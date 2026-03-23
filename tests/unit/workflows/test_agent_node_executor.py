"""AgentNodeExecutor mit synchronem Stub (kein Modell)."""

import pytest

from app.services.workflow_agent_adapter import set_workflow_agent_sync_override
from app.workflows.execution.context import AbortToken, RunContext
from app.workflows.execution.node_executors.agent import AgentNodeExecutor
from app.workflows.models.definition import WorkflowDefinition, WorkflowNode


def _ctx() -> RunContext:
    d = WorkflowDefinition("w", "w", [], [])
    return RunContext(run_id="r", definition=d, initial_input={}, abort=AbortToken())


@pytest.fixture(autouse=True)
def _clear_agent_override():
    yield
    set_workflow_agent_sync_override(None)


def test_agent_success_via_override():
    def stub(aid: str, prompt: str, model_override):
        assert aid == "ag1"
        assert "hello" in prompt
        return {
            "success": True,
            "response_text": "OK-OUT",
            "task_id": "t1",
            "metadata": {"m": 1},
        }

    set_workflow_agent_sync_override(stub)
    node = WorkflowNode("n", "agent", config={"agent_id": "ag1"})
    ex = AgentNodeExecutor()
    out = ex.execute(node, {"prompt_text": "hello world"}, _ctx())
    assert out["response_text"] == "OK-OUT"
    assert out["task_id"] == "t1"
    assert out["metadata"]["m"] == 1


def test_agent_failure_raises():
    def stub_fail(aid, prompt, mo):
        return {"success": False, "error": "agent kaputt"}

    set_workflow_agent_sync_override(stub_fail)
    node = WorkflowNode("n", "agent", config={"agent_id": "x"})
    ex = AgentNodeExecutor()
    with pytest.raises(RuntimeError, match="agent kaputt"):
        ex.execute(node, {"prompt_text": "p"}, _ctx())


def test_agent_missing_prompt():
    node = WorkflowNode("n", "agent", config={"agent_id": "x"})
    ex = AgentNodeExecutor()
    with pytest.raises(ValueError, match="prompt_text"):
        ex.execute(node, {}, _ctx())
