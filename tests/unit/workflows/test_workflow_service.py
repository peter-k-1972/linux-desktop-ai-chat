"""Tests für WorkflowService."""

import pytest

from app.core.db.database_manager import DatabaseManager
from app.services.workflow_service import (
    IncompleteHistoricalRunError,
    RunNotFoundError,
    WorkflowNotFoundError,
    WorkflowService,
    WorkflowValidationError,
    reset_workflow_service,
)
from app.workflows.models.run import WorkflowRun
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.status import WorkflowDefinitionStatus, WorkflowRunStatus


@pytest.fixture
def service(tmp_path):
    db_path = str(tmp_path / "svc.db")
    DatabaseManager(db_path, ensure_default_project=False)
    reset_workflow_service()
    return WorkflowService(WorkflowRepository(db_path))


def _valid_def(wid="w1"):
    return WorkflowDefinition(
        wid,
        "Test",
        [
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        [WorkflowEdge("a1", "s", "e")],
    )


def test_validate_and_save_sets_status(service):
    d = _valid_def()
    vr = service.save_workflow(d)
    assert vr.is_valid
    loaded = service.load_workflow("w1")
    assert loaded.status == WorkflowDefinitionStatus.VALID


def test_save_invalid_marks_invalid(service):
    d = WorkflowDefinition(
        "bad",
        "B",
        [WorkflowNode("s", "start"), WorkflowNode("e", "end")],
        [],
    )
    vr = service.save_workflow(d)
    assert not vr.is_valid
    loaded = service.load_workflow("bad")
    assert loaded.status == WorkflowDefinitionStatus.INVALID


def test_start_run(service):
    d = _valid_def("run_w")
    service.save_workflow(d)
    run = service.start_run("run_w", initial_input={"x": 1})
    assert run.status == WorkflowRunStatus.COMPLETED
    assert run.final_output == {"x": 1}
    again = service.get_run(run.run_id)
    assert again.status == WorkflowRunStatus.COMPLETED
    assert again.final_output == {"x": 1}
    assert len(again.node_runs) == 2


def test_run_history(service):
    d = _valid_def("hist")
    service.save_workflow(d)
    service.start_run("hist", {"n": 1})
    service.start_run("hist", {"n": 2})
    runs = service.list_runs(workflow_id="hist")
    assert len(runs) == 2


def test_list_node_runs_matches_get_run(service):
    d = _valid_def("lrn")
    service.save_workflow(d)
    run = service.start_run("lrn", {"k": 1})
    listed = service.list_node_runs(run.run_id)
    loaded = service.get_run(run.run_id)
    assert len(listed) == len(loaded.node_runs)
    assert {n.node_run_id for n in listed} == {n.node_run_id for n in loaded.node_runs}


def test_invalid_workflow_not_startable(service):
    d = WorkflowDefinition(
        "inv",
        "I",
        [WorkflowNode("s", "start")],
        [],
    )
    service.save_workflow(d)
    with pytest.raises(WorkflowValidationError):
        service.start_run("inv", {})


def test_load_missing(service):
    with pytest.raises(WorkflowNotFoundError):
        service.load_workflow("missing")


def test_cancel_pending_run(service):
    d = _valid_def("cnp")
    service.save_workflow(d)
    # kein echter PENDING ohne execute: simulieren via Repo
    from app.workflows.models.run import WorkflowRun

    run = WorkflowRun(
        run_id="pending_r",
        workflow_id="cnp",
        workflow_version=1,
        status=WorkflowRunStatus.PENDING,
        initial_input={},
        definition_snapshot=d.to_dict(),
    )
    service._repo.save_run(run)
    assert service.cancel_run("pending_r") is True
    got = service.get_run("pending_r")
    assert got.status == WorkflowRunStatus.CANCELLED


def test_duplicate_workflow(service):
    d = _valid_def("dup_src")
    service.save_workflow(d)
    dup = service.duplicate_workflow("dup_src", "dup_tgt", "Kopie-Name")
    assert dup.workflow_id == "dup_tgt"
    assert dup.name == "Kopie-Name"
    assert dup.version == 1
    again = service.load_workflow("dup_tgt")
    assert again.nodes[0].node_id == d.nodes[0].node_id


def test_list_workflows_respects_scope(service):
    ga = _valid_def("scope_g")
    ga.project_id = None
    pb = _valid_def("scope_p")
    pb.project_id = 3
    service.save_workflow(ga)
    service.save_workflow(pb)
    all_ids = {w.workflow_id for w in service.list_workflows()}
    assert "scope_g" in all_ids and "scope_p" in all_ids
    li = service.list_workflows(project_scope_id=3, include_global=True)
    assert {w.workflow_id for w in li} == {"scope_g", "scope_p"}
    li2 = service.list_workflows(project_scope_id=3, include_global=False)
    assert {w.workflow_id for w in li2} == {"scope_p"}


def test_duplicate_preserves_project_id(service):
    d = _valid_def("dup_p")
    d.project_id = 5
    service.save_workflow(d)
    dup = service.duplicate_workflow("dup_p", "dup_p2", "X")
    assert dup.project_id == 5


def test_cancel_completed_returns_false(service):
    d = _valid_def("cc_done")
    service.save_workflow(d)
    r = service.start_run("cc_done", {})
    assert r.status == WorkflowRunStatus.COMPLETED
    assert service.cancel_run(r.run_id) is False


def test_get_run_missing(service):
    with pytest.raises(RunNotFoundError):
        service.get_run("no_such_run")


def test_start_run_from_previous_uses_same_workflow_and_input(service):
    d = _valid_def("rerun_wf")
    service.save_workflow(d)
    first = service.start_run("rerun_wf", initial_input={"a": 1, "b": 2})
    assert first.workflow_id == "rerun_wf"
    second = service.start_run_from_previous(first.run_id)
    assert second.run_id != first.run_id
    assert second.workflow_id == "rerun_wf"
    assert second.initial_input == {"a": 1, "b": 2}
    again_first = service.get_run(first.run_id)
    assert again_first.initial_input == {"a": 1, "b": 2}
    assert again_first.run_id == first.run_id


def test_start_run_from_previous_override_input(service):
    d = _valid_def("rerun_ov")
    service.save_workflow(d)
    first = service.start_run("rerun_ov", {"k": "orig"})
    second = service.start_run_from_previous(first.run_id, initial_input_override={"k": "new"})
    assert second.initial_input == {"k": "new"}
    assert service.get_run(first.run_id).initial_input == {"k": "orig"}


def test_start_run_from_previous_missing_run(service):
    with pytest.raises(RunNotFoundError):
        service.start_run_from_previous("missing_run_id")


def test_start_run_from_previous_rejects_blank_workflow_id(service):
    d = _valid_def("blank_wf")
    service.save_workflow(d)
    bad = WorkflowRun(
        run_id="bad_rerun_src",
        workflow_id="   ",
        workflow_version=1,
        initial_input={"x": 1},
        definition_snapshot=d.to_dict(),
    )
    service._repo.save_run(bad)
    with pytest.raises(IncompleteHistoricalRunError):
        service.start_run_from_previous("bad_rerun_src")
