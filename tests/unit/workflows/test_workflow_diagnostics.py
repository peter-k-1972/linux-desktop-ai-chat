"""O2: Diagnose-Ableitung aus WorkflowRun / NodeRuns."""

from __future__ import annotations

from app.workflows.diagnostics import summarize_workflow_run
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.status import NodeRunStatus, WorkflowRunStatus


def _nr(
    nid: str,
    ntype: str,
    *,
    status: NodeRunStatus = NodeRunStatus.COMPLETED,
    err: str | None = None,
) -> NodeRun:
    return NodeRun(
        node_run_id=f"nr_{nid}",
        run_id="r1",
        node_id=nid,
        node_type=ntype,
        status=status,
        error_message=err,
    )


def test_completed_diagnosis():
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
        node_runs=[_nr("a", "noop")],
    )
    d = summarize_workflow_run(run)
    assert d.is_completed
    assert "Erfolgreich" in d.headline
    assert d.is_failed is False


def test_cancelled_diagnosis():
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.CANCELLED,
        error_message="user stop",
    )
    d = summarize_workflow_run(run)
    assert d.is_cancelled
    assert "Abgebrochen" in d.headline
    assert d.run_error == "user stop"


def test_failed_prioritizes_first_failed_node():
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.FAILED,
        error_message="run level",
        node_runs=[
            _nr("ok", "noop", status=NodeRunStatus.COMPLETED),
            _nr("bad", "agent", status=NodeRunStatus.FAILED, err="node boom"),
        ],
    )
    d = summarize_workflow_run(run)
    assert d.is_failed
    assert d.failed_node_id == "bad"
    assert d.failed_node_type == "agent"
    assert d.failed_node_error == "node boom"
    assert "bad" in d.headline
    assert d.run_error == "run level"


def test_failed_without_failed_node_uses_run_error():
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.FAILED,
        error_message="topo broke",
        node_runs=[_nr("x", "noop", status=NodeRunStatus.COMPLETED)],
    )
    d = summarize_workflow_run(run)
    assert d.failed_node_id is None
    assert "Kein Knoten" in d.summary or "ohne" in d.summary.lower()
    assert d.run_error == "topo broke"


def test_failed_no_node_no_run_error():
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.FAILED,
        node_runs=[],
    )
    d = summarize_workflow_run(run)
    assert d.is_failed
    assert d.run_error is None
    assert d.failed_node_id is None
    assert "ohne" in d.summary.lower()


def test_pending_diagnosis():
    run = WorkflowRun(
        run_id="r1",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.PENDING,
        node_runs=[],
    )
    d = summarize_workflow_run(run)
    assert d.is_pending_or_running
    assert "Ausstehend" in d.headline or "pending" in d.summary.lower()
