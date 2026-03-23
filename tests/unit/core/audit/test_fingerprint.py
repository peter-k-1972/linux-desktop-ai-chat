"""Fingerprint V1 für Incidents."""

import pytest

from app.core.audit.fingerprint import compute_incident_fingerprint, failure_fingerprint_inputs
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.status import NodeRunStatus, WorkflowRunStatus


def _failed_run(*, wid="wf1", node_id="n1", ntype="noop", node_err="boom", run_err=None):
    nr = NodeRun(
        node_run_id="nr1",
        run_id="r1",
        node_id=node_id,
        node_type=ntype,
        status=NodeRunStatus.FAILED,
        error_message=node_err,
    )
    return WorkflowRun(
        run_id="r1",
        workflow_id=wid,
        workflow_version=1,
        status=WorkflowRunStatus.FAILED,
        error_message=run_err,
        definition_snapshot={"project_id": None},
        node_runs=[nr],
    )


def test_fingerprint_stable_for_same_inputs():
    r1 = _failed_run()
    r2 = _failed_run()
    assert compute_incident_fingerprint(r1) == compute_incident_fingerprint(r2)


def test_fingerprint_differs_when_node_changes():
    a = _failed_run(node_id="a")
    b = _failed_run(node_id="b")
    assert compute_incident_fingerprint(a) != compute_incident_fingerprint(b)


def test_fingerprint_differs_when_error_text_changes():
    a = _failed_run(node_err="error one")
    b = _failed_run(node_err="error two")
    assert compute_incident_fingerprint(a) != compute_incident_fingerprint(b)


def test_fingerprint_rejects_non_failed():
    r = WorkflowRun(
        run_id="r1",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.COMPLETED,
        definition_snapshot={},
    )
    with pytest.raises(ValueError):
        compute_incident_fingerprint(r)


def test_failure_inputs_run_level_when_no_failed_node():
    r = WorkflowRun(
        run_id="r1",
        workflow_id="w",
        workflow_version=1,
        status=WorkflowRunStatus.FAILED,
        error_message="run level",
        definition_snapshot={},
        node_runs=[],
    )
    wid, nid, ntype, err = failure_fingerprint_inputs(r)
    assert wid == "w"
    assert nid is None
    assert ntype is None
    assert "run level" in err
