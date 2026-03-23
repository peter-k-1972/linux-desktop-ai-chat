"""Tests für WorkflowRepository (SQLite)."""

import json

import pytest

from app.core.db.database_manager import DatabaseManager
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.status import NodeRunStatus, WorkflowDefinitionStatus, WorkflowRunStatus


@pytest.fixture
def repo(tmp_path):
    db_path = str(tmp_path / "wf.db")
    DatabaseManager(db_path, ensure_default_project=False)
    return WorkflowRepository(db_path)


def test_save_load_workflow(repo):
    d = WorkflowDefinition(
        workflow_id="w1",
        name="One",
        description="d",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[WorkflowEdge("e1", "s", "e")],
        schema_version=2,
        status=WorkflowDefinitionStatus.VALID,
    )
    repo.save_workflow(d)
    loaded = repo.load_workflow("w1")
    assert loaded is not None
    assert loaded.workflow_id == "w1"
    assert loaded.schema_version == 2
    assert loaded.nodes[0].node_id == "s"
    assert loaded.status == WorkflowDefinitionStatus.VALID


def test_list_workflows(repo):
    a = WorkflowDefinition(
        "a",
        "A",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
    )
    b = WorkflowDefinition(
        "b",
        "B",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
    )
    repo.save_workflow(a)
    repo.save_workflow(b)
    lst = repo.list_workflows()
    assert {w.workflow_id for w in lst} == {"a", "b"}


def test_save_load_project_id(repo):
    d = WorkflowDefinition(
        "wp",
        "Proj",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
        project_id=42,
    )
    repo.save_workflow(d)
    loaded = repo.load_workflow("wp")
    assert loaded is not None
    assert loaded.project_id == 42


def test_list_workflows_scoped_and_include_global(repo):
    g = WorkflowDefinition(
        "glo",
        "G",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
        project_id=None,
    )
    p = WorkflowDefinition(
        "pr1",
        "P",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
        project_id=7,
    )
    repo.save_workflow(g)
    repo.save_workflow(p)
    all_w = repo.list_workflows()
    assert {w.workflow_id for w in all_w} == {"glo", "pr1"}
    scoped = repo.list_workflows(project_scope_id=7, include_global=True)
    assert {w.workflow_id for w in scoped} == {"glo", "pr1"}
    only_p = repo.list_workflows(project_scope_id=7, include_global=False)
    assert {w.workflow_id for w in only_p} == {"pr1"}


def test_delete_workflow(repo):
    d = WorkflowDefinition(
        "del",
        "D",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
    )
    repo.save_workflow(d)
    assert repo.delete_workflow("del") is True
    assert repo.load_workflow("del") is None
    assert repo.delete_workflow("del") is False


def test_run_and_node_roundtrip(repo):
    d = WorkflowDefinition(
        "w",
        "W",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
    )
    repo.save_workflow(d)
    snap = d.to_dict()
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
        initial_input={"i": 1},
        final_output={"o": 2},
        definition_snapshot=snap,
    )
    repo.save_run(run)
    nr = NodeRun(
        node_run_id="nr1",
        run_id="r1",
        node_id="s",
        node_type="start",
        status=NodeRunStatus.COMPLETED,
        input_payload=None,
        output_payload={"i": 1},
    )
    repo.save_node_run(nr)
    got = repo.get_run("r1")
    assert got is not None
    assert got.status == WorkflowRunStatus.COMPLETED
    assert got.initial_input == {"i": 1}
    assert got.final_output == {"o": 2}
    assert got.definition_snapshot["workflow_id"] == "w"
    assert len(got.node_runs) == 1
    assert got.node_runs[0].node_run_id == "nr1"
    assert got.node_runs[0].output_payload == {"i": 1}


def test_update_run_and_node_run(repo):
    d = WorkflowDefinition(
        "w",
        "W",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
    )
    repo.save_workflow(d)
    run = WorkflowRun(
        run_id="r2",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.PENDING,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    repo.save_run(run)
    nr = NodeRun(
        node_run_id="nr2",
        run_id="r2",
        node_id="s",
        node_type="start",
        status=NodeRunStatus.RUNNING,
        input_payload={},
    )
    repo.save_node_run(nr)
    nr.status = NodeRunStatus.COMPLETED
    nr.output_payload = {"done": True}
    repo.update_node_run(nr)
    run.status = WorkflowRunStatus.COMPLETED
    run.final_output = {"done": True}
    repo.update_run(run)
    got = repo.get_run("r2")
    assert got.status == WorkflowRunStatus.COMPLETED
    assert got.node_runs[0].status == NodeRunStatus.COMPLETED
    assert got.node_runs[0].output_payload == {"done": True}


def test_json_roundtrip_in_db(repo):
    d = WorkflowDefinition(
        "wj",
        "J",
        [
            WorkflowNode(
                "s",
                "start",
                title="T",
                description="D",
                config={"nested": {"a": [1, 2, 3]}},
                position={"x": 10.5, "y": -2.0},
            ),
            WorkflowNode("e", "end"),
        ],
        [WorkflowEdge("x", "s", "e", source_port="out", target_port="in", condition=None)],
    )
    repo.save_workflow(d)
    import sqlite3

    conn = sqlite3.connect(repo._db_path)
    cur = conn.cursor()
    cur.execute("SELECT definition_json FROM workflows WHERE workflow_id = ?", ("wj",))
    row = cur.fetchone()
    conn.close()
    data = json.loads(row[0])
    assert data["schema_version"] == d.schema_version
    assert data["nodes"][0]["position"] == {"x": 10.5, "y": -2.0}
    loaded = repo.load_workflow("wj")
    assert loaded.nodes[0].position == {"x": 10.5, "y": -2.0}


def test_list_runs_filter(repo):
    d = WorkflowDefinition(
        "w",
        "W",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [WorkflowEdge("x", "s", "e")],
    )
    repo.save_workflow(d)
    for rid in ("r_a", "r_b"):
        r = WorkflowRun(
            run_id=rid,
            workflow_id="w",
            workflow_version=1,
            status=WorkflowRunStatus.COMPLETED,
            initial_input={},
            definition_snapshot=d.to_dict(),
        )
        repo.save_run(r)
    all_r = repo.list_runs()
    assert len(all_r) >= 2
    w_only = repo.list_runs(workflow_id="w")
    assert {x.run_id for x in w_only} >= {"r_a", "r_b"}
