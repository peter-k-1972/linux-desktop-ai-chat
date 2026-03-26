"""Integration: Dev-Assist-Workflow (Datei lesen → Patch → pytest) mit Agent-Stubs."""

from __future__ import annotations

import json

import pytest

from app.agents.agent_repository import AgentRepository
from app.agents.seed_agents import ensure_seed_agents
from app.core.db.database_manager import DatabaseManager
from app.services.workflow_agent_adapter import set_workflow_agent_sync_override
from app.services.workflow_service import WorkflowService, reset_workflow_service
from app.workflows.dev_assist_definition import WORKFLOW_ID, build_dev_assist_workflow_definition
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.registry.node_registry import build_default_node_registry
from app.workflows.validation.graph_validator import GraphValidator
from app.workflows.status import WorkflowRunStatus


@pytest.fixture
def service(tmp_path):
    db_path = str(tmp_path / "dev_assist_wf.db")
    DatabaseManager(db_path, ensure_default_project=False)
    ensure_seed_agents(AgentRepository(db_path))
    reset_workflow_service()
    return WorkflowService(WorkflowRepository(db_path))


@pytest.fixture(autouse=True)
def _clear_agent_override():
    yield
    set_workflow_agent_sync_override(None)


def _dev_assist_agent_stub(agent_id: str, prompt: str, model_override):
    if "[DEV_ASSIST_PHASE=analysis]" in prompt:
        return {
            "success": True,
            "response_text": "Analyse: Einfache Konstantenänderung, geringes Risiko.",
            "task_id": "stub-an",
            "metadata": {},
        }
    if "[DEV_ASSIST_PHASE=plan]" in prompt:
        return {
            "success": True,
            "response_text": "Plan: x von 1 auf 2 setzen (replace_block).",
            "task_id": "stub-pl",
            "metadata": {},
        }
    if "[DEV_ASSIST_PHASE=develop]" in prompt:
        body = {
            "mode": "replace_block",
            "path": "target.py",
            "old_text": "x = 1",
            "new_text": "x = 2",
        }
        return {
            "success": True,
            "response_text": "```json\n" + json.dumps(body, ensure_ascii=False) + "\n```",
            "task_id": "stub-dev",
            "metadata": {},
        }
    if "[DEV_ASSIST_PHASE=review]" in prompt:
        return {
            "success": True,
            "response_text": "Review: Änderung nachvollziehbar; Tests grün erwartet.",
            "task_id": "stub-rev",
            "metadata": {},
        }
    if "[DEV_ASSIST_PHASE=document]" in prompt:
        return {
            "success": True,
            "response_text": "Doku: target.py — x auf 2 erhöht (Anforderung).",
            "task_id": "stub-doc",
            "metadata": {},
        }
    return {
        "success": True,
        "response_text": f"FALLBACK:{agent_id}",
        "task_id": "stub-x",
        "metadata": {},
    }


def test_dev_assist_definition_validates():
    d = build_dev_assist_workflow_definition()
    vr = GraphValidator().validate(d, build_default_node_registry())
    assert vr.is_valid, vr.errors


def test_dev_assist_run_read_patch_pytest(service, tmp_path):
    ws = tmp_path / "proj"
    ws.mkdir()
    (ws / "target.py").write_text("x = 1\n", encoding="utf-8")
    (ws / "test_target.py").write_text(
        "from pathlib import Path\n\n"
        "def test_x():\n"
        "    assert 'x = 2' in Path('target.py').read_text()\n",
        encoding="utf-8",
    )

    set_workflow_agent_sync_override(_dev_assist_agent_stub)
    d = build_dev_assist_workflow_definition()
    vr = service.save_workflow(d)
    assert vr.is_valid, vr.errors

    run = service.start_run(
        WORKFLOW_ID,
        {
            "workspace_root": str(ws),
            "target_file": "target.py",
            "problem_description": "Setze x auf 2.",
            "test_args": ["-q", "test_target.py"],
        },
    )
    assert run.status == WorkflowRunStatus.COMPLETED, (run.status, run.error_message)
    fo = run.final_output or {}
    assert fo.get("patch_applied") is True
    tr = fo.get("test_results")
    assert isinstance(tr, dict)
    assert tr.get("success") is True
    data = tr.get("data") or {}
    assert data.get("exit_code") == 0
    assert "analysis" in fo and "plan" in fo
    assert "documentation" in fo
    assert (ws / "target.py").read_text() == "x = 2\n"


def test_tool_call_python_failure_is_soft(service, tmp_path):
    """Regressionscheck: fehlgeschlagener python_callable bricht den Run nicht ab."""
    from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode

    d = WorkflowDefinition(
        workflow_id="wf_soft_py_tool",
        name="soft",
        nodes=[
            WorkflowNode("s", "start"),
            WorkflowNode(
                "t",
                "tool_call",
                config={
                    "executor_type": "python_callable",
                    "merge_step_output_into_payload": True,
                    "executor_config": {
                        "callable": "tests.unit.workflows.workflow_tool_stub.stub_fail_tool",
                    },
                },
            ),
            WorkflowNode("e", "end"),
        ],
        edges=[
            WorkflowEdge("a", "s", "t"),
            WorkflowEdge("b", "t", "e"),
        ],
    )
    service.save_workflow(d)
    run = service.start_run("wf_soft_py_tool", {})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert (run.final_output or {}).get("tool_call_success") is False
