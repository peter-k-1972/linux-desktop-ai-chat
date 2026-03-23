"""R4: DeploymentWorkspace Smoke."""

import pytest
from PySide6.QtWidgets import QApplication

from app.core.audit.repository import AuditRepository
from app.core.db.database_manager import DatabaseManager
from app.core.deployment.repository import DeploymentRepository
from app.gui.domains.operations.deployment.deployment_workspace import DeploymentWorkspace
from app.core.deployment.models import ReleaseLifecycle
from app.services.audit_service import AuditService
from app.services.deployment_operations_service import DeploymentOperationsService


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _patch_getter(monkeypatch, svc):
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: svc,
    )


@pytest.fixture
def dep_svc(tmp_path):
    p = str(tmp_path / "dw.db")
    DatabaseManager(p, ensure_default_project=False)
    audit = AuditService(AuditRepository(p))
    repo = DeploymentRepository(p)
    return DeploymentOperationsService(repo, audit)


def test_deployment_workspace_importable():
    assert DeploymentWorkspace is not None


def test_deployment_workspace_builds(monkeypatch, dep_svc):
    _app()
    _patch_getter(monkeypatch, dep_svc)
    w = DeploymentWorkspace()
    assert w.workspace_id == "deployment"
    assert w._tabs.count() == 3


def test_deployment_workspace_refresh_tabs(monkeypatch, dep_svc):
    _app()
    _patch_getter(monkeypatch, dep_svc)
    dep_svc.create_target(name="Host1")
    rel = dep_svc.create_release(display_name="App", version_label="0.1")
    dep_svc.update_release(
        release_id=rel.release_id,
        display_name="App",
        version_label="0.1",
        lifecycle_status=ReleaseLifecycle.READY,
    )
    w = DeploymentWorkspace()
    w._targets.refresh()
    assert w._targets._table.rowCount() >= 1
    w._releases.refresh()
    assert w._releases._list.rowCount() >= 1
    w._rollouts.refresh()
    assert w._rollouts._table.rowCount() == 0
