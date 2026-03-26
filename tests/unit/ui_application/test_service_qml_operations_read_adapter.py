"""ServiceQmlOperationsReadAdapter — stabile Serialisierung (gemockte Services)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.core.audit.models import AuditEventRecord, IncidentRecord
from app.ui_application.adapters.service_qml_operations_read_adapter import ServiceQmlOperationsReadAdapter


def test_adapter_list_audit_events_maps_record() -> None:
    ev = AuditEventRecord(
        id=3,
        occurred_at="t",
        event_type="workflow_started",
        actor="u",
        summary="s",
        payload_json=None,
        project_id=5,
        workflow_id="w",
        run_id="r",
        incident_id=None,
    )
    mock_audit = MagicMock()
    mock_audit.list_events.return_value = [ev]
    with patch(
        "app.ui_application.adapters.service_qml_operations_read_adapter.get_audit_service",
        return_value=mock_audit,
    ):
        ad = ServiceQmlOperationsReadAdapter()
        rows = ad.list_audit_events(limit=10, event_type=None)
    assert rows == [
        {
            "eventDbId": 3,
            "occurredAt": "t",
            "eventType": "workflow_started",
            "summary": "s",
            "actor": "u",
            "projectId": 5,
            "workflowId": "w",
            "runId": "r",
            "incidentId": -1,
        }
    ]


def test_adapter_platform_health_maps_checks() -> None:
    from app.qa.operations_models import HealthCheckResult, PlatformHealthSummary

    summary = PlatformHealthSummary(
        overall="warning",
        checked_at="iso",
        checks=[
            HealthCheckResult(check_id="x", severity="ok", title="T", detail="D"),
        ],
    )
    with patch(
        "app.ui_application.adapters.service_qml_operations_read_adapter.build_platform_health_summary",
        return_value=summary,
    ):
        ad = ServiceQmlOperationsReadAdapter()
        snap = ad.get_platform_health_snapshot()
    assert snap["overall"] == "warning"
    assert snap["checkedAt"] == "iso"
    assert snap["checks"][0]["checkId"] == "x"


def test_adapter_runtime_incident_detail() -> None:
    inc = IncidentRecord(
        id=7,
        status="open",
        severity="high",
        title="Hi",
        short_description="sd",
        workflow_run_id="wr",
        workflow_id="wf",
        project_id=None,
        first_seen_at="a",
        last_seen_at="b",
        occurrence_count=3,
        fingerprint="fp",
        diagnostic_code=None,
        resolution_note=None,
        created_at="c",
        updated_at="d",
    )
    mock_svc = MagicMock()
    mock_svc.get_incident.return_value = inc
    with patch(
        "app.ui_application.adapters.service_qml_operations_read_adapter.get_incident_service",
        return_value=mock_svc,
    ):
        ad = ServiceQmlOperationsReadAdapter()
        d = ad.get_runtime_incident(7)
    assert d is not None
    assert d["id"] == 7
    assert d["workflowRunId"] == "wr"
