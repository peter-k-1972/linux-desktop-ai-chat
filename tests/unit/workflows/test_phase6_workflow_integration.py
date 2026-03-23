"""Integrations-Workflows Phase 6 (Service + persistierte Runs, keine Netzwerk-Agenten)."""

import pytest

from app.core.db.database_manager import DatabaseManager
from app.services.workflow_agent_adapter import set_workflow_agent_sync_override
from app.services.workflow_service import WorkflowService, reset_workflow_service
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.status import WorkflowRunStatus


@pytest.fixture
def service(tmp_path):
    db_path = str(tmp_path / "p6.db")
    DatabaseManager(db_path, ensure_default_project=False)
    reset_workflow_service()
    return WorkflowService(WorkflowRepository(db_path))


@pytest.fixture(autouse=True)
def _agent_stub():
    def stub(aid, prompt, mo):
        return {
            "success": True,
            "response_text": f"REPLY:{prompt[:20]}",
            "task_id": "stub",
            "metadata": {},
        }

    set_workflow_agent_sync_override(stub)
    yield
    set_workflow_agent_sync_override(None)


def test_start_prompt_build_end(service):
    d = WorkflowDefinition(
        workflow_id="p6_pb",
        name="PB",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode(
                "p",
                "prompt_build",
                title="P",
                config={"template": "Hello {who}"},
            ),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("x1", "s", "p"),
            WorkflowEdge("x2", "p", "e"),
        ],
    )
    service.save_workflow(d)
    run = service.start_run("p6_pb", {"who": "World"})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert run.final_output is not None
    assert run.final_output.get("prompt_text") == "Hello World"
    again = service.get_run(run.run_id)
    assert len(again.node_runs) == 3
    assert again.node_runs[1].output_payload.get("prompt_text") == "Hello World"


def test_start_prompt_agent_end(service):
    d = WorkflowDefinition(
        workflow_id="p6_ag",
        name="AG",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode(
                "p",
                "prompt_build",
                title="P",
                config={"prompt_text": "Ask:{q}"},
            ),
            WorkflowNode("a", "agent", title="A", config={"agent_id": "dummy-agent"}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("x1", "s", "p"),
            WorkflowEdge("x2", "p", "a"),
            WorkflowEdge("x3", "a", "e"),
        ],
    )
    service.save_workflow(d)
    run = service.start_run("p6_ag", {"q": "why"})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert "REPLY:" in (run.final_output or {}).get("response_text", "")


def test_start_tool_call_end(service):
    d = WorkflowDefinition(
        workflow_id="p6_tc",
        name="TC",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode(
                "t",
                "tool_call",
                title="T",
                config={
                    "executor_type": "python_callable",
                    "executor_config": {
                        "callable": "tests.unit.workflows.workflow_tool_stub.stub_concat_tool",
                    },
                },
            ),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("x1", "s", "t"),
            WorkflowEdge("x2", "t", "e"),
        ],
    )
    service.save_workflow(d)
    run = service.start_run("p6_tc", {"a": "x", "b": "y"})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert (run.final_output or {}).get("tool_result", {}).get("tool_result") == "xy"


def test_validation_rejects_bad_prompt_build(service):
    d = WorkflowDefinition(
        workflow_id="bad_pb",
        name="B",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("p", "prompt_build", title="P", config={}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("x1", "s", "p"),
            WorkflowEdge("x2", "p", "e"),
        ],
    )
    vr = service.validate_workflow(d)
    assert not vr.is_valid
    assert any("prompt_build" in e.lower() or "template" in e.lower() for e in vr.errors)


def test_validation_rejects_tool_call_without_executor(service):
    d = WorkflowDefinition(
        workflow_id="bad_tc",
        name="B",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("t", "tool_call", title="T", config={}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("x1", "s", "t"),
            WorkflowEdge("x2", "t", "e"),
        ],
    )
    vr = service.validate_workflow(d)
    assert not vr.is_valid
    assert any("executor_type" in e.lower() for e in vr.errors)


def test_validation_rejects_agent_without_ref(service):
    d = WorkflowDefinition(
        workflow_id="bad_ag",
        name="B",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("a", "agent", title="A", config={}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("x1", "s", "a"),
            WorkflowEdge("x2", "a", "e"),
        ],
    )
    vr = service.validate_workflow(d)
    assert not vr.is_valid
    assert any("agent" in e.lower() for e in vr.errors)


def test_validation_rejects_agent_both_id_and_slug(service):
    d = WorkflowDefinition(
        workflow_id="bad_ag2",
        name="B",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode(
                "a",
                "agent",
                title="A",
                config={"agent_id": "a1", "agent_slug": "s1"},
            ),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("x1", "s", "a"),
            WorkflowEdge("x2", "a", "e"),
        ],
    )
    vr = service.validate_workflow(d)
    assert not vr.is_valid
