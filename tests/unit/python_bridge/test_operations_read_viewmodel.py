"""OperationsReadViewModel — deterministische Refresh-/Selektionspfade (Fake-Port, kein DB-Zwang)."""

from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import QObject, Slot

from python_bridge.operations.operations_read_viewmodel import OperationsReadViewModel


class _FakeOpsPort:
    def __init__(self) -> None:
        self.audit_calls = 0
        self.inc_calls = 0
        self.qa_calls = 0
        self.platform_calls = 0
        self.get_incident_calls: list[int] = []

    def list_audit_events(self, *, limit: int, event_type: Optional[str]) -> list[dict[str, Any]]:
        self.audit_calls += 1
        return [
            {
                "eventDbId": 9,
                "occurredAt": "2026-01-01T00:00:00Z",
                "eventType": "workflow_started",
                "summary": "started",
                "actor": "a",
                "projectId": 1,
                "workflowId": "w1",
                "runId": "r1",
                "incidentId": -1,
            }
        ]

    def list_runtime_incidents(self, *, status: Optional[str], limit: int) -> list[dict[str, Any]]:
        self.inc_calls += 1
        return [
            {
                "incidentId": 42,
                "lastSeenAt": "t",
                "status": "open",
                "severity": "high",
                "title": "T",
                "workflowId": "wf",
                "runId": "runX",
                "occurrenceCount": 2,
            }
        ]

    def get_runtime_incident(self, incident_id: int) -> Optional[dict[str, Any]]:
        self.get_incident_calls.append(incident_id)
        if incident_id != 42:
            return None
        return {
            "id": 42,
            "status": "open",
            "severity": "high",
            "title": "T",
            "shortDescription": "desc",
            "workflowRunId": "runX",
            "workflowId": "wf",
            "projectId": 7,
            "firstSeenAt": "a",
            "lastSeenAt": "b",
            "occurrenceCount": 2,
            "fingerprint": "fp",
            "diagnosticCode": "",
            "resolutionNote": "",
            "createdAt": "c",
            "updatedAt": "d",
        }

    def load_qa_incident_index_snapshot(self) -> dict[str, Any]:
        self.qa_calls += 1
        return {
            "hasData": True,
            "incidentCount": 1,
            "openCount": 1,
            "boundCount": 0,
            "replayReadyCount": 0,
            "warnings": [],
            "incidents": [
                {
                    "incidentId": "qa-1",
                    "title": "QA",
                    "status": "open",
                    "severity": "low",
                    "subsystem": "s",
                    "failureClass": "f",
                    "bindingText": "b",
                }
            ],
        }

    def load_audit_followup_snapshot(self) -> dict[str, Any]:
        return {
            "hasData": True,
            "byCategory": {"mittel": 1},
            "items": [
                {
                    "category": "mittel",
                    "source": "x.py",
                    "description": "fixme",
                    "location": "10",
                }
            ],
        }

    def get_platform_health_snapshot(self) -> dict[str, Any]:
        self.platform_calls += 1
        return {
            "overall": "ok",
            "checkedAt": "iso",
            "checks": [{"checkId": "c1", "severity": "ok", "title": "T", "detail": "D"}],
        }


class _ShellStub(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[str, str, str]] = []

    @Slot(str, str, str)
    def requestRouteChangeWithContextJson(self, area: str, ws: str, ctx: str) -> None:
        self.calls.append((area, ws, ctx))


def test_operations_read_refresh_all_populates_models(qapplication) -> None:
    port = _FakeOpsPort()
    vm = OperationsReadViewModel(port)
    try:
        vm.refreshAll()
        assert port.audit_calls == 1 and port.inc_calls == 1 and port.qa_calls == 1
        assert port.platform_calls == 1
        assert vm.auditEvents.rowCount() == 1
        assert vm.runtimeIncidents.rowCount() == 1
        assert vm.qaIndexIncidents.rowCount() == 1
        assert vm.auditFollowups.rowCount() == 1
        assert vm.platformChecks.rowCount() == 1
        assert "QA-Index" in vm.qaSummaryLine
        assert vm.canNavigateIncidentRun is False
    finally:
        vm.dispose()


def test_select_runtime_incident_enables_navigation_and_shell_call(qapplication) -> None:
    port = _FakeOpsPort()
    vm = OperationsReadViewModel(port)
    shell = _ShellStub()
    try:
        vm.refreshRuntimeIncidents()
        vm.selectRuntimeIncidentRow(0)
        assert vm.canNavigateIncidentRun is True
        assert port.get_incident_calls == [42]
        vm.navigateSelectedIncidentToWorkflow(shell)
        assert len(shell.calls) == 1
        area, ws, raw = shell.calls[0]
        assert area == "operations" and ws == "operations_workflows"
        assert "workflow_ops_run_id" in raw and "runX" in raw
        assert "workflow_ops_workflow_id" in raw and "wf" in raw
    finally:
        vm.dispose()


def test_operations_read_viewmodel_module_has_no_sqlalchemy() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    src = (root / "python_bridge/operations/operations_read_viewmodel.py").read_text(encoding="utf-8")
    assert "sqlalchemy" not in src.lower()
