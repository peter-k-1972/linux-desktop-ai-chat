"""Phase 6b: context_load + chain_delegate (Adapter, Validierung, Integrationspfade)."""

from __future__ import annotations

import uuid

import pytest

from app.services.workflow_context_adapter import set_workflow_context_build_override
from app.services.workflow_agent_adapter import set_workflow_agent_sync_override
from app.services.workflow_orchestration_adapter import (
    run_workflow_orchestration,
    set_workflow_orchestration_override,
)
from app.workflows.execution.context import AbortToken
from app.workflows.execution.executor import WorkflowExecutor
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.models.run import WorkflowRun
from app.workflows.registry.node_registry import build_default_node_registry
from app.workflows.status import WorkflowRunStatus
from app.workflows.validation.graph_validator import GraphValidator


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    set_workflow_context_build_override(None)
    set_workflow_orchestration_override(None)
    set_workflow_agent_sync_override(None)


def test_context_load_override_success():
    def fake_bundle(
        chat_id: int,
        *,
        request_context_hint=None,
        context_policy=None,
        include_payload_preview=True,
        include_trace=False,
    ):
        return {
            "context_payload": {"stub": True, "chat_id": chat_id},
            "context_text": "preview-lines",
            "metadata": {
                "chat_id": chat_id,
                "request_context_hint": request_context_hint,
                "context_policy": context_policy,
            },
        }

    set_workflow_context_build_override(fake_bundle)
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="C",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("c", "context_load", title="C", config={"chat_id": 42}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "c"),
            WorkflowEdge("a2", "c", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r_ctx",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.COMPLETED
    assert run.final_output["context_text"] == "preview-lines"
    assert run.final_output["context_payload"]["stub"] is True


def test_context_load_validation_invalid_hint():
    reg = build_default_node_registry()
    d = WorkflowDefinition(
        workflow_id="w",
        name="X",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode(
                "c",
                "context_load",
                title="C",
                config={"chat_id": 1, "request_context_hint": "not_a_real_hint"},
            ),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "c"),
            WorkflowEdge("a2", "c", "e"),
        ],
    )
    r = GraphValidator().validate(d, reg)
    assert not r.is_valid
    assert any("request_context_hint" in e for e in r.errors)


def test_context_load_runtime_missing_chat_id():
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="X",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("c", "context_load", title="C", config={}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "c"),
            WorkflowEdge("a2", "c", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r_x",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.FAILED
    assert "chat_id" in (run.error_message or "").lower()


def test_chain_delegate_override_success():
    def fake_orch(prompt, mode, model_override=None, planner_model=None):
        return {
            "result_text": f"ok:{prompt[:10]}",
            "aggregated_output": f"ok:{prompt[:10]}",
            "graph_summary": {"tasks": [], "task_count": 0},
            "delegation_metadata": {"mode": mode},
            "subresults": [],
        }

    set_workflow_orchestration_override(fake_orch)
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="Ch",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("d", "chain_delegate", title="D", config={"mode": "plan_only"}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "d"),
            WorkflowEdge("a2", "d", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r_ch",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={"prompt_text": "Hello delegation"},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.COMPLETED
    assert run.final_output["result_text"].startswith("ok:Hello dele")


def test_chain_delegate_override_failure():
    def boom(prompt, mode, model_override=None, planner_model=None):
        raise RuntimeError("delegation_absichtlich")

    set_workflow_orchestration_override(boom)
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="Ch",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("d", "chain_delegate", title="D"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "d"),
            WorkflowEdge("a2", "d", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r_fail",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={"prompt_text": "x"},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.FAILED
    assert "delegation_absichtlich" in (run.error_message or "")


def test_orchestration_plan_only_real_no_network():
    out = run_workflow_orchestration("Einfache Testaufgabe ohne Netz", mode="plan_only")
    assert out["graph_summary"]["task_count"] >= 1
    assert "result_text" in out
    assert out["delegation_metadata"].get("mode") == "plan_only"


def test_orchestration_execute_real_with_agent_stub_no_network():
    """Echter Planner+ExecutionEngine-Pfad; Agent über workflow_agent_adapter-Stub (kein Modell)."""
    set_workflow_agent_sync_override(
        lambda agent_id, prompt, model_override: {
            "success": True,
            "response_text": f"stub:{(prompt or '')[:40]}",
        }
    )
    try:
        out = run_workflow_orchestration("Eine kurze Aufgabe", mode="execute")
    finally:
        set_workflow_agent_sync_override(None)
    assert out["delegation_metadata"].get("mode") == "execute"
    assert "stub:" in (out.get("result_text") or "")


def test_integration_start_context_prompt_end():
    set_workflow_context_build_override(
        lambda chat_id, **kw: {
            "context_payload": {"ok": True},
            "context_text": "CTX-BODY",
            "metadata": {"chat_id": chat_id},
        }
    )
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="I",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("c", "context_load", title="C", config={"chat_id": 1}),
            WorkflowNode(
                "p",
                "prompt_build",
                title="P",
                config={"template": "Say: {context_text}"},
            ),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "c"),
            WorkflowEdge("a2", "c", "p"),
            WorkflowEdge("a3", "p", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r_i1",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.COMPLETED
    assert "CTX-BODY" in run.final_output.get("prompt_text", "")


def test_integration_start_prompt_chain_end():
    set_workflow_orchestration_override(
        lambda prompt, mode, model_override=None, planner_model=None: {
            "result_text": f"delegated:{prompt}",
            "aggregated_output": f"delegated:{prompt}",
            "graph_summary": {"tasks": [], "task_count": 0},
            "delegation_metadata": {},
            "subresults": [],
        }
    )
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="I2",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode(
                "p",
                "prompt_build",
                title="P",
                config={"prompt_text": "Task: run pipeline"},
            ),
            WorkflowNode("d", "chain_delegate", title="D"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "p"),
            WorkflowEdge("a2", "p", "d"),
            WorkflowEdge("a3", "d", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r_i2",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.COMPLETED
    assert "delegated:Task: run pipeline" in run.final_output.get("result_text", "")


def test_integration_start_context_agent_end():
    set_workflow_context_build_override(
        lambda chat_id, **kw: {
            "context_payload": {},
            "context_text": "Use this context",
            "metadata": {},
        }
    )
    set_workflow_agent_sync_override(
        lambda agent_id, prompt, model_override: {
            "success": True,
            "response_text": f"agent:{prompt[:30]}",
        }
    )
    reg = build_default_node_registry()
    ex = WorkflowExecutor(node_run_id_factory=lambda: f"n_{uuid.uuid4().hex[:8]}")
    d = WorkflowDefinition(
        workflow_id="w",
        name="I3",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("c", "context_load", title="C", config={"chat_id": 1}),
            WorkflowNode(
                "a",
                "agent",
                title="A",
                config={"agent_id": "any-id"},
            ),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "c"),
            WorkflowEdge("a2", "c", "a"),
            WorkflowEdge("a3", "a", "e"),
        ],
    )
    run = WorkflowRun(
        run_id="r_i3",
        workflow_id=d.workflow_id,
        workflow_version=1,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    ex.execute(d, run, reg, AbortToken())
    assert run.status == WorkflowRunStatus.COMPLETED
    assert "Use this context" in (run.final_output.get("response_text") or "")


def test_chain_delegate_validation_bad_mode():
    reg = build_default_node_registry()
    d = WorkflowDefinition(
        workflow_id="w",
        name="X",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("d", "chain_delegate", title="D", config={"mode": "parallel_magic"}),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[
            WorkflowEdge("a1", "s", "d"),
            WorkflowEdge("a2", "d", "e"),
        ],
    )
    r = GraphValidator().validate(d, reg)
    assert not r.is_valid
    assert any("chain_delegate" in e for e in r.errors)
