"""R1: ProjectService schreibt Audit-Einträge."""

from app.core.audit.models import AuditEventType
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.services.audit_service import get_audit_service, reset_audit_service
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, set_project_service


def test_project_crud_audit(tmp_path):
    db_path = str(tmp_path / "pr.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = AppSettings(backend=InMemoryBackend())
    set_infrastructure(infra)
    reset_audit_service()
    set_project_service(ProjectService())
    try:
        svc = ProjectService()
        pid = svc.create_project("Alpha")
        rows = get_audit_service().list_events(event_type=AuditEventType.PROJECT_CREATED)
        assert len(rows) == 1
        assert rows[0].project_id == pid

        svc.update_project(pid, name="Beta")
        assert len(get_audit_service().list_events(event_type=AuditEventType.PROJECT_UPDATED)) == 1

        svc.delete_project(pid)
        assert len(get_audit_service().list_events(event_type=AuditEventType.PROJECT_DELETED)) == 1
    finally:
        set_project_service(None)
        set_infrastructure(None)
        reset_audit_service()


def test_update_project_no_op_no_project_updated_audit(tmp_path):
    """Kein SQL-UPDATE ohne SET-Klausel → kein Phantom PROJECT_UPDATED."""
    db_path = str(tmp_path / "pr2.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = AppSettings(backend=InMemoryBackend())
    set_infrastructure(infra)
    reset_audit_service()
    set_project_service(ProjectService())
    try:
        svc = ProjectService()
        pid = svc.create_project("NoOp")
        assert len(get_audit_service().list_events(event_type=AuditEventType.PROJECT_UPDATED)) == 0
        svc.update_project(pid)
        assert len(get_audit_service().list_events(event_type=AuditEventType.PROJECT_UPDATED)) == 0
        svc.update_project(pid, name="Changed")
        assert len(get_audit_service().list_events(event_type=AuditEventType.PROJECT_UPDATED)) == 1
    finally:
        set_project_service(None)
        set_infrastructure(None)
        reset_audit_service()
