"""AuditRepository — SQLite."""

from app.core.audit.models import AuditEventType, IncidentRecord, IncidentSeverity, IncidentStatus
from app.core.audit.repository import AuditRepository
from app.core.db.database_manager import DatabaseManager


def test_append_and_list_audit(tmp_path):
    p = str(tmp_path / "a.db")
    DatabaseManager(p, ensure_default_project=False)
    r = AuditRepository(p)
    r.append_audit_event(event_type=AuditEventType.PROJECT_CREATED, summary="x", project_id=3)
    rows = r.list_audit_events(project_id=3)
    assert len(rows) == 1
    assert rows[0].event_type == AuditEventType.PROJECT_CREATED


def test_incident_insert_and_recurrence(tmp_path):
    p = str(tmp_path / "i.db")
    DatabaseManager(p, ensure_default_project=False)
    r = AuditRepository(p)
    now = "2025-01-01T12:00:00+00:00"
    rec = IncidentRecord(
        id=None,
        status=IncidentStatus.OPEN,
        severity=IncidentSeverity.MEDIUM,
        title="t",
        short_description="d",
        workflow_run_id="run_a",
        workflow_id="wf",
        project_id=None,
        first_seen_at=now,
        last_seen_at=now,
        occurrence_count=1,
        fingerprint="fp1",
        diagnostic_code="dc",
        resolution_note=None,
        created_at=now,
        updated_at=now,
    )
    iid = r.insert_incident(rec)
    assert iid > 0
    r.update_incident_recurrence(
        "fp1",
        workflow_run_id="run_b",
        last_seen_at="2025-01-02T12:00:00+00:00",
        updated_at="2025-01-02T12:00:00+00:00",
        short_description="d2",
    )
    cur = r.get_incident_by_fingerprint("fp1")
    assert cur is not None
    assert cur.occurrence_count == 2
    assert cur.workflow_run_id == "run_b"
