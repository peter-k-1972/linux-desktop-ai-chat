"""
Phase 7 – Referenz-Workflows: Service + Persistenz (kein GUI, keine Netzwerk-Agenten).

Abdeckt die in der Abnahme genannten linearen DAGs mit realen Node-Typen.
"""

from __future__ import annotations

import pytest

from app.core.db.database_manager import DatabaseManager
from app.services.workflow_agent_adapter import set_workflow_agent_sync_override
from app.services.workflow_context_adapter import set_workflow_context_build_override
from app.services.workflow_orchestration_adapter import set_workflow_orchestration_override
from app.services.workflow_service import WorkflowService, reset_workflow_service
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.status import WorkflowRunStatus


@pytest.fixture
def service(tmp_path):
    db_path = str(tmp_path / "ref7.db")
    DatabaseManager(db_path, ensure_default_project=False)
    reset_workflow_service()
    return WorkflowService(WorkflowRepository(db_path))


@pytest.fixture(autouse=True)
def _stubs():
    def agent_stub(aid, prompt, mo):
        return {"success": True, "response_text": f"R:{(prompt or '')[:24]}", "metadata": {}}

    def ctx_stub(chat_id, **kw):
        return {
            "context_payload": {"chat_id": chat_id},
            "context_text": "CTX",
            "metadata": {},
        }

    def orch_stub(prompt, mode=None, model_override=None, planner_model=None):
        return {
            "result_text": f"ORCH:{(prompt or '')[:20]}",
            "aggregated_output": f"ORCH:{(prompt or '')[:20]}",
            "graph_summary": {"tasks": [], "task_count": 0},
            "delegation_metadata": {"mode": mode or "execute"},
            "subresults": [],
        }

    set_workflow_agent_sync_override(agent_stub)
    set_workflow_context_build_override(ctx_stub)
    set_workflow_orchestration_override(orch_stub)
    yield
    set_workflow_agent_sync_override(None)
    set_workflow_context_build_override(None)
    set_workflow_orchestration_override(None)


def test_ref_start_end(service):
    d = WorkflowDefinition(
        workflow_id="ref_se",
        name="ref_se",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[WorkflowEdge("only", "s", "e")],
    )
    service.save_workflow(d)
    run = service.start_run("ref_se", {"k": 1})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert run.final_output == {"k": 1}
    persisted = service.get_run(run.run_id)
    assert len(persisted.node_runs) == 2


def test_ref_start_noop_end(service):
    d = WorkflowDefinition(
        workflow_id="ref_sne",
        name="ref_sne",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("n", "noop", title="N", config={"merge": {"x": 2}}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a", "s", "n"),
            WorkflowEdge("b", "n", "e"),
        ],
    )
    service.save_workflow(d)
    run = service.start_run("ref_sne", {"a": 1})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert run.final_output.get("x") == 2


def test_ref_start_prompt_build_end(service):
    d = WorkflowDefinition(
        workflow_id="ref_spb",
        name="ref_spb",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode(
                "p",
                "prompt_build",
                title="P",
                config={"template": "Hi {name}"},
            ),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a", "s", "p"),
            WorkflowEdge("b", "p", "e"),
        ],
    )
    service.save_workflow(d)
    run = service.start_run("ref_spb", {"name": "Ada"})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert "Ada" in (run.final_output or {}).get("prompt_text", "")


def test_ref_start_prompt_agent_end(service):
    d = WorkflowDefinition(
        workflow_id="ref_spa",
        name="ref_spa",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("p", "prompt_build", title="P", config={"prompt_text": "Q:{q}"}),
            WorkflowNode("a", "agent", title="A", config={"agent_id": "id1"}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a", "s", "p"),
            WorkflowEdge("b", "p", "a"),
            WorkflowEdge("c", "a", "e"),
        ],
    )
    service.save_workflow(d)
    run = service.start_run("ref_spa", {"q": "ping"})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert "R:" in (run.final_output or {}).get("response_text", "")


def test_ref_start_tool_call_end(service):
    d = WorkflowDefinition(
        workflow_id="ref_stc",
        name="ref_stc",
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
            WorkflowEdge("a", "s", "t"),
            WorkflowEdge("b", "t", "e"),
        ],
    )
    service.save_workflow(d)
    run = service.start_run("ref_stc", {"a": "1", "b": "2"})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert (run.final_output or {}).get("tool_result", {}).get("tool_result") == "12"


def test_ref_start_context_load_end(service):
    d = WorkflowDefinition(
        workflow_id="ref_scl",
        name="ref_scl",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("c", "context_load", title="C", config={"chat_id": 1}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a", "s", "c"),
            WorkflowEdge("b", "c", "e"),
        ],
    )
    service.save_workflow(d)
    run = service.start_run("ref_scl", {})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert (run.final_output or {}).get("context_text") == "CTX"


def test_ref_start_prompt_chain_delegate_end(service):
    d = WorkflowDefinition(
        workflow_id="ref_spcd",
        name="ref_spcd",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("p", "prompt_build", title="P", config={"prompt_text": "Do:{t}"}),
            WorkflowNode("d", "chain_delegate", title="D", config={"mode": "plan_only"}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a", "s", "p"),
            WorkflowEdge("b", "p", "d"),
            WorkflowEdge("c", "d", "e"),
        ],
    )
    service.save_workflow(d)
    run = service.start_run("ref_spcd", {"t": "task"})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert "ORCH:" in (run.final_output or {}).get("result_text", "")
