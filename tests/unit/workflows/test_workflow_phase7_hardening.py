"""Phase 7: robuste Deserialisierung, Repository bei defekten Daten, Randfälle."""

from __future__ import annotations

import sqlite3

import pytest

from app.core.db.database_manager import DatabaseManager
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.status import NodeRunStatus, WorkflowRunStatus


@pytest.fixture
def repo(tmp_path):
    db_path = str(tmp_path / "wf7.db")
    DatabaseManager(db_path, ensure_default_project=False)
    return WorkflowRepository(db_path)


def test_node_run_from_dict_invalid_status_defaults_pending():
    nr = NodeRun.from_dict(
        {
            "node_run_id": "n1",
            "run_id": "r1",
            "node_id": "x",
            "node_type": "noop",
            "status": "not_a_real_status",
        }
    )
    assert nr.status == NodeRunStatus.PENDING


def test_workflow_run_from_dict_invalid_status_defaults_pending():
    wr = WorkflowRun.from_dict(
        {
            "run_id": "r1",
            "workflow_id": "w",
            "workflow_version": 1,
            "status": "broken",
            "initial_input": {},
            "definition_snapshot": {},
        }
    )
    assert wr.status == WorkflowRunStatus.PENDING


def test_list_workflows_skips_corrupt_definition_json(repo):
    good = WorkflowDefinition(
        "ok",
        "OK",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
    )
    repo.save_workflow(good)
    conn = sqlite3.connect(repo._db_path)
    conn.execute(
        """
        INSERT INTO workflows (
            workflow_id, name, description, version, schema_version,
            definition_status, definition_json, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        ("bad", "Bad", "", 1, 1, "invalid", '{"nodes":[]}'),
    )
    conn.commit()
    conn.close()
    lst = repo.list_workflows()
    assert len(lst) == 1
    assert lst[0].workflow_id == "ok"


def test_get_run_tolerates_corrupt_status_in_db(repo):
    d = WorkflowDefinition(
        "w",
        "W",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
    )
    repo.save_workflow(d)
    run = WorkflowRun(
        run_id="r_bad_st",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    repo.save_run(run)
    conn = sqlite3.connect(repo._db_path)
    conn.execute("UPDATE workflow_runs SET status = ? WHERE run_id = ?", ("__corrupt__", "r_bad_st"))
    conn.commit()
    conn.close()
    got = repo.get_run("r_bad_st")
    assert got is not None
    assert got.status == WorkflowRunStatus.PENDING


def test_list_node_runs_tolerates_corrupt_node_status(repo):
    d = WorkflowDefinition(
        "w",
        "W",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
    )
    repo.save_workflow(d)
    run = WorkflowRun(
        run_id="r_n",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    repo.save_run(run)
    nr = NodeRun(
        node_run_id="nr_x",
        run_id="r_n",
        node_id="s",
        node_type="start",
        status=NodeRunStatus.COMPLETED,
    )
    repo.save_node_run(nr)
    conn = sqlite3.connect(repo._db_path)
    conn.execute(
        "UPDATE workflow_node_runs SET status = ? WHERE node_run_id = ?",
        ("__bad__", "nr_x"),
    )
    conn.commit()
    conn.close()
    rows = repo.list_node_runs("r_n")
    assert len(rows) == 1
    assert rows[0].status == NodeRunStatus.PENDING
