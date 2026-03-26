"""Adapter: :class:`QmlOperationsReadPort` → Audit-, Incident-Service, OperationsAdapter, Platform Health."""

from __future__ import annotations

from typing import Any, Optional

from app.qa.operations_adapter import OperationsAdapter
from app.services.audit_service import get_audit_service
from app.services.incident_service import get_incident_service
from app.services.platform_health_service import build_platform_health_summary


def _binding_text(binding: Any, replay: Any) -> str:
    parts: list[str] = []
    if binding is not None:
        parts.append(f"binding={binding!r}")
    if replay is not None:
        parts.append(f"replay={replay!r}")
    return " · ".join(parts) if parts else ""


class ServiceQmlOperationsReadAdapter:
    def __init__(self, *, operations_adapter: OperationsAdapter | None = None) -> None:
        self._qa = operations_adapter or OperationsAdapter()

    def list_audit_events(
        self,
        *,
        limit: int,
        event_type: Optional[str],
    ) -> list[dict[str, Any]]:
        cap = max(1, min(int(limit), 2000))
        rows = get_audit_service().list_events(event_type=event_type, limit=cap)
        out: list[dict[str, Any]] = []
        for e in rows:
            out.append(
                {
                    "eventDbId": e.id if e.id is not None else -1,
                    "occurredAt": e.occurred_at or "",
                    "eventType": e.event_type or "",
                    "summary": e.summary or "",
                    "actor": e.actor or "",
                    "projectId": -1 if e.project_id is None else int(e.project_id),
                    "workflowId": e.workflow_id or "",
                    "runId": e.run_id or "",
                    "incidentId": -1 if e.incident_id is None else int(e.incident_id),
                }
            )
        return out

    def list_runtime_incidents(
        self,
        *,
        status: Optional[str],
        limit: int,
    ) -> list[dict[str, Any]]:
        cap = max(1, min(int(limit), 2000))
        rows = get_incident_service().list_incidents(status=status, limit=cap)
        out: list[dict[str, Any]] = []
        for inc in rows:
            out.append(
                {
                    "incidentId": int(inc.id) if inc.id is not None else -1,
                    "lastSeenAt": inc.last_seen_at or "",
                    "status": inc.status or "",
                    "severity": inc.severity or "",
                    "title": inc.title or "",
                    "workflowId": inc.workflow_id or "",
                    "runId": inc.workflow_run_id or "",
                    "occurrenceCount": int(inc.occurrence_count),
                }
            )
        return out

    def get_runtime_incident(self, incident_id: int) -> Optional[dict[str, Any]]:
        inc = get_incident_service().get_incident(int(incident_id))
        if inc is None:
            return None
        return {
            "id": int(inc.id) if inc.id is not None else -1,
            "status": inc.status or "",
            "severity": inc.severity or "",
            "title": inc.title or "",
            "shortDescription": inc.short_description or "",
            "workflowRunId": inc.workflow_run_id or "",
            "workflowId": inc.workflow_id or "",
            "projectId": -1 if inc.project_id is None else int(inc.project_id),
            "firstSeenAt": inc.first_seen_at or "",
            "lastSeenAt": inc.last_seen_at or "",
            "occurrenceCount": int(inc.occurrence_count),
            "fingerprint": inc.fingerprint or "",
            "diagnosticCode": inc.diagnostic_code or "",
            "resolutionNote": inc.resolution_note or "",
            "createdAt": inc.created_at or "",
            "updatedAt": inc.updated_at or "",
        }

    def load_qa_incident_index_snapshot(self) -> dict[str, Any]:
        data = self._qa.load_incident_operations()
        inc_rows: list[dict[str, Any]] = []
        for x in data.incidents:
            inc_rows.append(
                {
                    "incidentId": x.incident_id,
                    "title": x.title,
                    "status": x.status,
                    "severity": x.severity,
                    "subsystem": x.subsystem,
                    "failureClass": x.failure_class,
                    "bindingText": _binding_text(x.binding_status, x.replay_status),
                }
            )
        return {
            "hasData": data.has_data,
            "incidentCount": int(data.incident_count),
            "openCount": int(data.open_count),
            "boundCount": int(data.bound_count),
            "replayReadyCount": int(data.replay_ready_count),
            "warnings": list(data.warnings),
            "incidents": inc_rows,
        }

    def load_audit_followup_snapshot(self) -> dict[str, Any]:
        data = self._qa.load_audit_operations()
        items: list[dict[str, Any]] = []
        for it in data.items:
            items.append(
                {
                    "category": it.category,
                    "source": it.source,
                    "description": it.description,
                    "location": it.location,
                }
            )
        by_cat = {k: int(v) for k, v in data.by_category.items()}
        return {
            "hasData": data.has_data,
            "byCategory": by_cat,
            "items": items,
        }

    def get_platform_health_snapshot(self) -> dict[str, Any]:
        summary = build_platform_health_summary()
        checks: list[dict[str, Any]] = []
        for c in summary.checks:
            checks.append(
                {
                    "checkId": c.check_id,
                    "severity": c.severity,
                    "title": c.title,
                    "detail": c.detail,
                }
            )
        return {
            "overall": summary.overall,
            "checkedAt": summary.checked_at,
            "checks": checks,
        }
