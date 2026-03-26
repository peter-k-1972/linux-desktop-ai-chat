"""Bridge-ViewModel: Operations Read (Audit, Incidents, QA-Datei, Platform) — kein Service in QML."""

from __future__ import annotations

import json
import logging
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.core.navigation.nav_areas import NavArea
from app.ui_application.adapters.service_qml_operations_read_adapter import ServiceQmlOperationsReadAdapter
from app.ui_application.ports.qml_operations_read_port import QmlOperationsReadPort
from python_bridge.operations.operations_read_models import (
    AuditEventRowModel,
    AuditFollowupRowModel,
    PlatformCheckRowModel,
    QaIndexIncidentRowModel,
    RuntimeIncidentRowModel,
)

logger = logging.getLogger(__name__)

_WORKSPACE_WORKFLOWS = "operations_workflows"
_AUDIT_LIMIT = 800
_INCIDENT_LIMIT = 800


class OperationsReadViewModel(QObject):
    lastErrorChanged = Signal()
    detailCaptionChanged = Signal()
    detailBodyChanged = Signal()
    qaSummaryLineChanged = Signal()
    auditFollowupSummaryChanged = Signal()
    platformHeadlineChanged = Signal()
    busyChanged = Signal()
    canNavigateIncidentRunChanged = Signal()

    def __init__(self, port: QmlOperationsReadPort, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._port = port
        self._busy = False
        self._last_error = ""
        self._detail_caption = "—"
        self._detail_body = ""
        self._qa_summary = "—"
        self._audit_followup_summary = "—"
        self._platform_headline = "—"
        self._audit_events = AuditEventRowModel(self)
        self._runtime_incidents = RuntimeIncidentRowModel(self)
        self._qa_index_rows = QaIndexIncidentRowModel(self)
        self._audit_followups = AuditFollowupRowModel(self)
        self._platform_checks = PlatformCheckRowModel(self)
        self._qa_row_cache: list[dict[str, Any]] = []
        self._followup_row_cache: list[dict[str, Any]] = []
        self._selected_runtime_incident_id = -1
        self._nav_run_id = ""
        self._nav_workflow_id = ""

    def _get_busy(self) -> bool:
        return self._busy

    busy = Property(bool, _get_busy, notify=busyChanged)

    def _get_last_error(self) -> str:
        return self._last_error

    lastError = Property(str, _get_last_error, notify=lastErrorChanged)

    def _get_detail_caption(self) -> str:
        return self._detail_caption

    detailCaption = Property(str, _get_detail_caption, notify=detailCaptionChanged)

    def _get_detail_body(self) -> str:
        return self._detail_body

    detailBody = Property(str, _get_detail_body, notify=detailBodyChanged)

    def _get_qa_summary(self) -> str:
        return self._qa_summary

    qaSummaryLine = Property(str, _get_qa_summary, notify=qaSummaryLineChanged)

    def _get_audit_followup_summary(self) -> str:
        return self._audit_followup_summary

    auditFollowupSummary = Property(str, _get_audit_followup_summary, notify=auditFollowupSummaryChanged)

    def _get_platform_headline(self) -> str:
        return self._platform_headline

    platformHeadline = Property(str, _get_platform_headline, notify=platformHeadlineChanged)

    def _get_audit_events(self) -> AuditEventRowModel:
        return self._audit_events

    auditEvents = Property(QObject, _get_audit_events, constant=True)

    def _get_runtime_incidents(self) -> RuntimeIncidentRowModel:
        return self._runtime_incidents

    runtimeIncidents = Property(QObject, _get_runtime_incidents, constant=True)

    def _get_qa_index_rows(self) -> QaIndexIncidentRowModel:
        return self._qa_index_rows

    qaIndexIncidents = Property(QObject, _get_qa_index_rows, constant=True)

    def _get_audit_followups(self) -> AuditFollowupRowModel:
        return self._audit_followups

    auditFollowups = Property(QObject, _get_audit_followups, constant=True)

    def _get_platform_checks(self) -> PlatformCheckRowModel:
        return self._platform_checks

    platformChecks = Property(QObject, _get_platform_checks, constant=True)

    def _get_can_navigate_incident_run(self) -> bool:
        return bool(self._nav_run_id.strip() and self._nav_workflow_id.strip())

    canNavigateIncidentRun = Property(bool, _get_can_navigate_incident_run, notify=canNavigateIncidentRunChanged)

    def _set_busy(self, v: bool) -> None:
        if self._busy != v:
            self._busy = v
            self.busyChanged.emit()

    def _set_error(self, msg: str) -> None:
        t = msg or ""
        if self._last_error != t:
            self._last_error = t
            self.lastErrorChanged.emit()

    def _set_detail(self, caption: str, body: str) -> None:
        c = caption or "—"
        b = body or ""
        if self._detail_caption != c:
            self._detail_caption = c
            self.detailCaptionChanged.emit()
        if self._detail_body != b:
            self._detail_body = b
            self.detailBodyChanged.emit()

    def _set_nav_targets(self, run_id: str, workflow_id: str) -> None:
        r = run_id or ""
        w = workflow_id or ""
        if self._nav_run_id != r or self._nav_workflow_id != w:
            self._nav_run_id = r
            self._nav_workflow_id = w
            self.canNavigateIncidentRunChanged.emit()

    @Slot()
    def refreshAuditEvents(self) -> None:
        self._set_busy(True)
        try:
            rows = self._port.list_audit_events(limit=_AUDIT_LIMIT, event_type=None)
            self._audit_events.set_rows([dict(x) for x in rows])
            self._set_error("")
        except Exception as e:
            logger.exception("refreshAuditEvents")
            self._set_error(str(e))
            self._audit_events.set_rows([])
        finally:
            self._set_busy(False)

    @Slot()
    def refreshRuntimeIncidents(self) -> None:
        self._set_busy(True)
        try:
            rows = self._port.list_runtime_incidents(status=None, limit=_INCIDENT_LIMIT)
            self._runtime_incidents.set_rows([dict(x) for x in rows])
            self._selected_runtime_incident_id = -1
            self._set_detail("—", "")
            self._set_nav_targets("", "")
            self._set_error("")
        except Exception as e:
            logger.exception("refreshRuntimeIncidents")
            self._set_error(str(e))
            self._runtime_incidents.set_rows([])
        finally:
            self._set_busy(False)

    @Slot()
    def refreshQaFileSnapshots(self) -> None:
        self._set_busy(True)
        try:
            snap = self._port.load_qa_incident_index_snapshot()
            inc_list = snap.get("incidents") or []
            self._qa_row_cache = [dict(x) for x in inc_list]
            self._qa_index_rows.set_rows(self._qa_row_cache)
            if snap.get("hasData"):
                self._qa_summary = (
                    f"QA-Index: {snap.get('incidentCount', 0)} Einträge · "
                    f"offen {snap.get('openCount', 0)} · "
                    f"gebunden {snap.get('boundCount', 0)} · "
                    f"replay-ready {snap.get('replayReadyCount', 0)}"
                )
            else:
                self._qa_summary = "QA-Index: keine Daten (docs/qa/incidents/index.json)."
            w = snap.get("warnings") or []
            if w:
                self._qa_summary += "\nWarnungen: " + "; ".join(str(x) for x in w[:5])
            self.qaSummaryLineChanged.emit()

            fol = self._port.load_audit_followup_snapshot()
            items = fol.get("items") or []
            self._followup_row_cache = [dict(x) for x in items]
            self._audit_followups.set_rows(self._followup_row_cache)
            by_cat = fol.get("byCategory") or {}
            if fol.get("hasData") and by_cat:
                parts = [f"{k}: {v}" for k, v in sorted(by_cat.items())]
                self._audit_followup_summary = "AUDIT_REPORT Follow-ups nach Kategorie: " + ", ".join(parts)
            elif fol.get("hasData"):
                self._audit_followup_summary = "AUDIT_REPORT: keine tabellarischen Follow-ups."
            else:
                self._audit_followup_summary = "Kein AUDIT_REPORT.md oder leer."
            self.auditFollowupSummaryChanged.emit()
            self._set_error("")
        except Exception as e:
            logger.exception("refreshQaFileSnapshots")
            self._set_error(str(e))
        finally:
            self._set_busy(False)

    @Slot()
    def refreshPlatformHealth(self) -> None:
        self._set_busy(True)
        try:
            snap = self._port.get_platform_health_snapshot()
            checks = snap.get("checks") or []
            self._platform_checks.set_rows([dict(x) for x in checks])
            self._platform_headline = f"Gesamt: {snap.get('overall', '—')} · {snap.get('checkedAt', '')}"
            self.platformHeadlineChanged.emit()
            self._set_error("")
        except Exception as e:
            logger.exception("refreshPlatformHealth")
            self._set_error(str(e))
            self._platform_checks.set_rows([])
        finally:
            self._set_busy(False)

    @Slot()
    def refreshAll(self) -> None:
        self.refreshAuditEvents()
        self.refreshRuntimeIncidents()
        self.refreshQaFileSnapshots()
        self.refreshPlatformHealth()

    @Slot(int)
    def selectAuditEventRow(self, row: int) -> None:
        if row < 0 or row >= self._audit_events.rowCount():
            self._set_detail("—", "")
            return
        idx = self._audit_events.index(row, 0)
        parts = [
            f"Zeit: {self._audit_events.data(idx, AuditEventRowModel.OccurredAtRole)}",
            f"Typ: {self._audit_events.data(idx, AuditEventRowModel.EventTypeRole)}",
            f"Projekt: {self._audit_events.data(idx, AuditEventRowModel.ProjectIdRole)}",
            f"Workflow: {self._audit_events.data(idx, AuditEventRowModel.WorkflowIdRole)}",
            f"Run: {self._audit_events.data(idx, AuditEventRowModel.RunIdRole)}",
            "",
            str(self._audit_events.data(idx, AuditEventRowModel.SummaryRole) or ""),
        ]
        self._set_detail("Audit-Ereignis", "\n".join(parts))
        self._set_nav_targets("", "")

    @Slot(int)
    def selectRuntimeIncidentRow(self, row: int) -> None:
        if row < 0 or row >= self._runtime_incidents.rowCount():
            self._selected_runtime_incident_id = -1
            self._set_detail("—", "")
            self._set_nav_targets("", "")
            return
        idx = self._runtime_incidents.index(row, 0)
        iid = int(self._runtime_incidents.data(idx, RuntimeIncidentRowModel.IncidentIdRole) or -1)
        run_id = str(self._runtime_incidents.data(idx, RuntimeIncidentRowModel.RunIdRole) or "")
        wf_id = str(self._runtime_incidents.data(idx, RuntimeIncidentRowModel.WorkflowIdRole) or "")
        self._selected_runtime_incident_id = iid
        self._set_nav_targets(run_id, wf_id)
        if iid < 0:
            self._set_detail("—", "")
            return
        try:
            d = self._port.get_runtime_incident(iid)
            if not d:
                self._set_detail(f"Incident #{iid}", "Nicht gefunden.")
                return
            body = "\n".join(
                [
                    d.get("shortDescription") or "",
                    "",
                    f"Fingerprint: {d.get('fingerprint') or ''}",
                    f"Diagnosecode: {d.get('diagnosticCode') or '—'}",
                    f"Notiz: {d.get('resolutionNote') or '—'}",
                    f"Vorkommen: {d.get('occurrenceCount')}",
                ]
            )
            self._set_detail(f"#{d.get('id')} — {d.get('title')}", body.strip())
            self._set_error("")
        except Exception as e:
            logger.exception("selectRuntimeIncidentRow")
            self._set_error(str(e))
            self._set_detail("Incident", str(e))

    @Slot(int)
    def selectQaIndexRow(self, row: int) -> None:
        if row < 0 or row >= len(self._qa_row_cache):
            self._set_detail("—", "")
            return
        r = self._qa_row_cache[row]
        body = "\n".join(
            [
                f"ID: {r.get('incidentId')}",
                f"Status: {r.get('status')}",
                f"Schwere: {r.get('severity')}",
                f"Subsystem: {r.get('subsystem')}",
                f"Failure: {r.get('failureClass')}",
                f"Bindings: {r.get('bindingText')}",
            ]
        )
        self._set_detail(str(r.get("title") or "QA-Index"), body)
        self._set_nav_targets("", "")

    @Slot(int)
    def selectAuditFollowupRow(self, row: int) -> None:
        if row < 0 or row >= len(self._followup_row_cache):
            self._set_detail("—", "")
            return
        r = self._followup_row_cache[row]
        body = "\n".join(
            [
                f"Kategorie: {r.get('category')}",
                f"Datei: {r.get('source')}",
                f"Ort: {r.get('location')}",
                "",
                str(r.get("description") or ""),
            ]
        )
        self._set_detail("Audit Follow-up", body.strip())
        self._set_nav_targets("", "")

    @Slot(int)
    def selectPlatformCheckRow(self, row: int) -> None:
        if row < 0 or row >= self._platform_checks.rowCount():
            self._set_detail("—", "")
            return
        idx = self._platform_checks.index(row, 0)
        title = str(self._platform_checks.data(idx, PlatformCheckRowModel.TitleRole) or "")
        sev = str(self._platform_checks.data(idx, PlatformCheckRowModel.SeverityRole) or "")
        det = str(self._platform_checks.data(idx, PlatformCheckRowModel.DetailRole) or "")
        cid = str(self._platform_checks.data(idx, PlatformCheckRowModel.CheckIdRole) or "")
        self._set_detail(f"{title} ({sev})", f"{cid}\n\n{det}".strip())
        self._set_nav_targets("", "")

    @Slot("QVariant")
    def navigateSelectedIncidentToWorkflow(self, shell_obj: Any) -> None:
        """Nutzt dieselben Pending-Context-Schlüssel wie die Widget-GUI (``operations_context``)."""
        if not self._nav_run_id.strip() or not self._nav_workflow_id.strip():
            self._set_error("Kein Workflow/Run am gewählten Incident.")
            return
        if shell_obj is None:
            self._set_error("Shell nicht angebunden.")
            return
        try:
            ctx = {
                "workflow_ops_run_id": self._nav_run_id.strip(),
                "workflow_ops_workflow_id": self._nav_workflow_id.strip(),
            }
            raw = json.dumps(ctx, separators=(",", ":"), sort_keys=True)
            fn = getattr(shell_obj, "requestRouteChangeWithContextJson", None)
            if not callable(fn):
                self._set_error("Shell unterstützt keine Kontext-Navigation.")
                return
            fn(NavArea.OPERATIONS, _WORKSPACE_WORKFLOWS, raw)
            self._set_error("")
        except Exception as e:
            logger.exception("navigateSelectedIncidentToWorkflow")
            self._set_error(str(e))

    @Slot()
    def dispose(self) -> None:
        pass


def build_operations_read_viewmodel(
    port: QmlOperationsReadPort | None = None,
) -> OperationsReadViewModel:
    return OperationsReadViewModel(port or ServiceQmlOperationsReadAdapter())
