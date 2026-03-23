"""O1: list_run_summaries ohne NodeRun-Eager-Load."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.core.db.database_manager import DatabaseManager
from app.services.workflow_service import WorkflowService
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.models.run import WorkflowRun
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.status import WorkflowDefinitionStatus, WorkflowRunStatus


@pytest.fixture
def repo(tmp_path):
    db_path = str(tmp_path / "wf_sum.db")
    DatabaseManager(db_path, ensure_default_project=False)
    return WorkflowRepository(db_path)


def _minimal_wf(wid: str, name: str, *, project_id: int | None) -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_id=wid,
        name=name,
        description="",
        nodes=[
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        edges=[WorkflowEdge("x", "s", "e")],
        status=WorkflowDefinitionStatus.VALID,
        project_id=project_id,
    )


def test_list_run_summaries_workflow_filter_and_sort(repo):
    repo.save_workflow(_minimal_wf("w1", "W One", project_id=1))
    r_old = WorkflowRun(
        run_id="r_old",
        workflow_id="w1",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
    )
    r_new = WorkflowRun(
        run_id="r_new",
        workflow_id="w1",
        workflow_version=1,
        status=WorkflowRunStatus.FAILED,
        error_message="boom",
    )
    repo.save_run(r_old)
    repo.save_run(r_new)
    # älter / jünger (SQLite sort)
    import sqlite3

    with sqlite3.connect(repo._db_path) as conn:
        conn.execute(
            "UPDATE workflow_runs SET created_at = datetime('now', '-10 days'), "
            "started_at = datetime('now', '-10 days'), finished_at = datetime('now', '-10 days') "
            "WHERE run_id = 'r_old'"
        )
        conn.execute(
            "UPDATE workflow_runs SET created_at = datetime('now', '-1 days'), "
            "started_at = datetime('now', '-1 days'), finished_at = datetime('now', '-1 days') "
            "WHERE run_id = 'r_new'"
        )
        conn.commit()

    with patch.object(repo, "list_node_runs", side_effect=AssertionError("kein NodeRun-Load in Summary")):
        sums = repo.list_run_summaries(workflow_id="w1", limit=50)

    assert len(sums) == 2
    assert sums[0].run_id == "r_new"
    assert sums[0].workflow_name == "W One"
    assert sums[0].project_id == 1
    assert sums[0].status == "failed"
    assert sums[0].error_message == "boom"
    assert sums[1].run_id == "r_old"


def test_list_run_summaries_project_filter_excludes_other_project(repo):
    repo.save_workflow(_minimal_wf("wa", "A", project_id=10))
    repo.save_workflow(_minimal_wf("wb", "B", project_id=20))
    for wid in ("wa", "wb"):
        repo.save_run(
            WorkflowRun(
                run_id=f"r_{wid}",
                workflow_id=wid,
                workflow_version=1,
                status=WorkflowRunStatus.COMPLETED,
            )
        )
    sums = repo.list_run_summaries(project_id=10, limit=50)
    assert {s.run_id for s in sums} == {"r_wa"}


def test_list_run_summaries_global_workflow_in_all_mode(repo):
    repo.save_workflow(_minimal_wf("glob", "G", project_id=None))
    repo.save_run(
        WorkflowRun(
            run_id="rg",
            workflow_id="glob",
            workflow_version=1,
            status=WorkflowRunStatus.COMPLETED,
        )
    )
    sums_proj = repo.list_run_summaries(project_id=99, limit=50)
    assert sums_proj == []
    sums_all = repo.list_run_summaries(limit=50)
    assert len(sums_all) == 1
    assert sums_all[0].project_id is None
    assert sums_all[0].workflow_id == "glob"


def test_list_run_summaries_status_filter(repo):
    repo.save_workflow(_minimal_wf("w", "W", project_id=None))
    repo.save_run(
        WorkflowRun(
            run_id="r_ok",
            workflow_id="w",
            workflow_version=1,
            status=WorkflowRunStatus.COMPLETED,
        )
    )
    repo.save_run(
        WorkflowRun(
            run_id="r_bad",
            workflow_id="w",
            workflow_version=1,
            status=WorkflowRunStatus.FAILED,
        )
    )
    failed_only = repo.list_run_summaries(workflow_id="w", status="failed", limit=50)
    assert [s.run_id for s in failed_only] == ["r_bad"]


def test_list_run_summaries_limit_offset(repo):
    repo.save_workflow(_minimal_wf("w", "W", project_id=None))
    for i in range(5):
        repo.save_run(
            WorkflowRun(
                run_id=f"r{i}",
                workflow_id="w",
                workflow_version=1,
                status=WorkflowRunStatus.COMPLETED,
            )
        )
    import sqlite3

    with sqlite3.connect(repo._db_path) as conn:
        for i in range(5):
            conn.execute(
                f"UPDATE workflow_runs SET finished_at = datetime('now', '-{i} hours') "
                f"WHERE run_id = 'r{i}'"
            )
        conn.commit()
    page0 = repo.list_run_summaries(workflow_id="w", limit=2, offset=0)
    page1 = repo.list_run_summaries(workflow_id="w", limit=2, offset=2)
    ids0 = {s.run_id for s in page0}
    ids1 = {s.run_id for s in page1}
    assert len(page0) == 2
    assert len(page1) == 2
    assert ids0.isdisjoint(ids1)


def test_workflow_service_list_run_summaries_delegates(tmp_path):
    db_path = str(tmp_path / "svc.db")
    DatabaseManager(db_path, ensure_default_project=False)
    repo = WorkflowRepository(db_path)
    svc = WorkflowService(repo)
    repo.save_workflow(_minimal_wf("w", "W", project_id=None))
    repo.save_run(
        WorkflowRun(
            run_id="r1",
            workflow_id="w",
            workflow_version=1,
            status=WorkflowRunStatus.COMPLETED,
        )
    )
    out = svc.list_run_summaries(workflow_id="w", limit=500)
    assert len(out) == 1
    assert out[0].run_id == "r1"
