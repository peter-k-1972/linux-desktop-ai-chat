"""R1: WorkflowService schreibt Audit und Incidents (optional injiziert)."""

from app.core.audit.models import AuditEventType
from app.core.audit.repository import AuditRepository
from app.core.db.database_manager import DatabaseManager
from app.services.audit_service import AuditService
from app.services.incident_service import IncidentService
from app.services.workflow_service import WorkflowService
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.status import WorkflowRunStatus


def _r1_service(tmp_path):
    db_path = str(tmp_path / "r1wf.db")
    DatabaseManager(db_path, ensure_default_project=False)
    repo = AuditRepository(db_path)
    audit = AuditService(repo)
    inc = IncidentService(repo, audit)
    svc = WorkflowService(
        WorkflowRepository(db_path),
        audit_service=audit,
        incident_service=inc,
    )
    return svc, audit, inc


def _ok_def(wid="w_ok"):
    return WorkflowDefinition(
        wid,
        "OK",
        [
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("e", "end", title="E"),
        ],
        [WorkflowEdge("a1", "s", "e")],
    )


def _fail_def(wid="w_fail"):
    return WorkflowDefinition(
        wid,
        "Fail",
        [
            WorkflowNode("s", "start", title="S"),
            WorkflowNode("c", "context_load", title="C", config={}),
            WorkflowNode("e", "end", title="E"),
        ],
        [
            WorkflowEdge("a1", "s", "c"),
            WorkflowEdge("a2", "c", "e"),
        ],
    )


def test_completed_run_emits_workflow_started_audit(tmp_path):
    svc, audit, _inc = _r1_service(tmp_path)
    d = _ok_def()
    svc.save_workflow(d)
    svc.start_run(d.workflow_id, {"x": 1})
    rows = audit.list_events(event_type=AuditEventType.WORKFLOW_STARTED)
    assert len(rows) == 1
    assert rows[0].workflow_id == d.workflow_id


def test_failed_run_emits_incident(tmp_path):
    svc, audit, inc = _r1_service(tmp_path)
    d = _fail_def()
    svc.save_workflow(d)
    run = svc.start_run(d.workflow_id, {})
    assert run.status == WorkflowRunStatus.FAILED
    lst = inc.list_incidents()
    assert len(lst) == 1
    assert lst[0].workflow_run_id == run.run_id
    created = audit.list_events(event_type=AuditEventType.INCIDENT_CREATED)
    assert len(created) == 1


def test_rerun_audit_type(tmp_path):
    svc, audit, _inc = _r1_service(tmp_path)
    d = _ok_def("w_r")
    svc.save_workflow(d)
    first = svc.start_run(d.workflow_id, {})
    assert first.status == WorkflowRunStatus.COMPLETED
    second = svc.start_run_from_previous(first.run_id)
    assert second.status == WorkflowRunStatus.COMPLETED
    reruns = audit.list_events(event_type=AuditEventType.WORKFLOW_RERUN_STARTED)
    assert len(reruns) == 1
    starts = audit.list_events(event_type=AuditEventType.WORKFLOW_STARTED)
    assert len(starts) == 1
