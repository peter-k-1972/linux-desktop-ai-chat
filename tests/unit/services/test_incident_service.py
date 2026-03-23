from app.core.audit.models import AuditEventType, IncidentStatus
from app.core.audit.repository import AuditRepository
from app.core.db.database_manager import DatabaseManager
from app.services.audit_service import AuditService
from app.services.incident_service import IncidentService
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.status import NodeRunStatus, WorkflowRunStatus


def _failed_run(run_id="r1", wid="wf_fail"):
    nr = NodeRun(
        node_run_id="nr1",
        run_id=run_id,
        node_id="bad",
        node_type="noop",
        status=NodeRunStatus.FAILED,
        error_message="same error",
    )
    return WorkflowRun(
        run_id=run_id,
        workflow_id=wid,
        workflow_version=1,
        status=WorkflowRunStatus.FAILED,
        definition_snapshot={"workflow_id": wid, "project_id": 7},
        node_runs=[nr],
    )


def test_sync_creates_and_upserts(tmp_path):
    p = str(tmp_path / "inc.db")
    DatabaseManager(p, ensure_default_project=False)
    repo = AuditRepository(p)
    audit = AuditService(repo)
    inc_svc = IncidentService(repo, audit)
    r1 = _failed_run("run_one")
    iid1 = inc_svc.sync_from_failed_run(r1)
    assert iid1 is not None
    r2 = _failed_run("run_two")
    iid2 = inc_svc.sync_from_failed_run(r2)
    assert iid2 == iid1
    cur = inc_svc.get_incident(iid1)
    assert cur is not None
    assert cur.occurrence_count == 2
    assert cur.workflow_run_id == "run_two"
    aud = audit.list_events(event_type=AuditEventType.INCIDENT_CREATED)
    assert len(aud) == 1


def test_set_status_audits_only_on_change(tmp_path):
    p = str(tmp_path / "st.db")
    DatabaseManager(p, ensure_default_project=False)
    repo = AuditRepository(p)
    audit = AuditService(repo)
    inc_svc = IncidentService(repo, audit)
    iid = inc_svc.sync_from_failed_run(_failed_run())
    before = len(audit.list_events(event_type=AuditEventType.INCIDENT_STATUS_CHANGED))
    inc_svc.set_status(iid, IncidentStatus.ACKNOWLEDGED)
    after = len(audit.list_events(event_type=AuditEventType.INCIDENT_STATUS_CHANGED))
    assert after == before + 1
    inc_svc.set_status(iid, IncidentStatus.ACKNOWLEDGED)
    assert len(audit.list_events(event_type=AuditEventType.INCIDENT_STATUS_CHANGED)) == after
