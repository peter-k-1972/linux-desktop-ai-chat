from app.core.audit.models import AuditEventType
from app.core.audit.repository import AuditRepository
from app.core.db.database_manager import DatabaseManager
from app.services.audit_service import AuditService


def test_record_and_filter(tmp_path):
    p = str(tmp_path / "aud.db")
    DatabaseManager(p, ensure_default_project=False)
    svc = AuditService(AuditRepository(p))
    svc.record_project_created(project_id=5, name="P")
    svc.record_workflow_started(
        run_id="r1", workflow_id="w1", project_id=5, is_rerun=False
    )
    rows = svc.list_events(event_type=AuditEventType.PROJECT_CREATED)
    assert len(rows) == 1
    assert rows[0].project_id == 5
