"""
Workflow-QML: Run-Scopes, Tabellenzeilen und Diagnose-Texte über den Canvas-Port.

Keine Qt-Abhängigkeit — spiegelt ``WorkflowsWorkspace`` / ``WorkflowRunPanel``-Semantik.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from app.workflows.diagnostics import format_diagnostic_preview, summarize_workflow_run
from app.workflows.models.run_summary import WorkflowRunSummary

if TYPE_CHECKING:
    from app.ui_application.ports.qml_workflow_canvas_port import QmlWorkflowCanvasPort
    from app.workflows.models.run import WorkflowRun

RUN_SCOPE_WORKFLOW = "workflow"
RUN_SCOPE_PROJECT = "project"
RUN_SCOPE_ALL = "all"


def _fmt_run_duration(started_at: datetime | None, finished_at: datetime | None) -> str:
    if started_at is None or finished_at is None:
        return "—"
    try:
        sec = int((finished_at - started_at).total_seconds())
    except Exception:
        return "—"
    if sec < 0:
        return "—"
    if sec < 1:
        return "<1s"
    if sec < 60:
        return f"{sec}s"
    m, s = divmod(sec, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


class WorkflowStudioPresenter:
    def __init__(self, port: QmlWorkflowCanvasPort) -> None:
        self._port = port

    @staticmethod
    def parse_initial_input_json(text: str) -> tuple[Optional[dict[str, Any]], Optional[str]]:
        """
        Entspricht :class:`app.gui.domains.operations.workflows.dialogs.workflow_input_dialog.WorkflowInputDialog`:
        leerer Text -> ``{}``; gültiges JSON-Objekt; sonst Fehlertext.
        """
        raw = (text or "").strip()
        if not raw:
            return {}, None
        try:
            val = json.loads(raw)
        except json.JSONDecodeError as e:
            return None, str(e)
        if not isinstance(val, dict):
            return None, "Es muss ein JSON-Objekt sein."
        return val, None

    def fetch_run_summaries(
        self,
        run_scope: str,
        *,
        loaded_workflow_id: str | None,
        status_filter: str | None,
        limit: int = 50,
    ) -> tuple[list[WorkflowRunSummary], str, str]:
        st = status_filter if status_filter else None
        scope = (run_scope or RUN_SCOPE_WORKFLOW).strip().lower()
        lim = max(1, min(int(limit), 500))

        if scope == RUN_SCOPE_WORKFLOW:
            if not loaded_workflow_id:
                return (
                    [],
                    "Modus: Dieser Workflow — kein Workflow geladen.",
                    "Bitte einen Workflow in der Liste auswählen.",
                )
            caption = f"Modus: Dieser Workflow (ID {loaded_workflow_id})."
            sums = self._port.list_run_summaries(
                workflow_id=loaded_workflow_id, status=st, limit=lim
            )
            empty = "Keine Runs für die aktuelle Filterkombination." if not sums else ""
            return sums, caption, empty

        if scope == RUN_SCOPE_PROJECT:
            pid = self._port.get_active_project_id()
            if pid is None:
                return (
                    [],
                    "Modus: Aktives Projekt — kein Projekt aktiv.",
                    "Aktivieren Sie ein Projekt (z. B. über Projekte oder die TopBar).",
                )
            caption = (
                f"Modus: Aktives Projekt (project_id={pid}). "
                "Nur Runs von Workflows mit dieser Projektzuordnung (nicht globale Workflows)."
            )
            sums = self._port.list_run_summaries(project_id=pid, status=st, limit=lim)
            empty = "Keine Runs für die aktuelle Filterkombination." if not sums else ""
            return sums, caption, empty

        caption = "Modus: Alle Runs — alle Workflows inkl. globaler Definitionen."
        sums = self._port.list_run_summaries(status=st, limit=lim)
        empty = "Keine Runs für die aktuelle Filterkombination." if not sums else ""
        return sums, caption, empty

    def run_summary_rows(self, sums: list[WorkflowRunSummary]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for s in sums:
            rows.append(
                {
                    "runId": s.run_id,
                    "status": s.status,
                    "duration": _fmt_run_duration(s.started_at, s.finished_at),
                    "started": s.started_at.isoformat() if s.started_at else "",
                    "workflowId": s.workflow_id,
                    "workflowName": s.workflow_name or "",
                    "projectLabel": "Global" if s.project_id is None else str(int(s.project_id)),
                    "errorPreview": format_diagnostic_preview(s.error_message, max_len=120),
                }
            )
        return rows

    def diagnostics_for_run(self, run: WorkflowRun) -> dict[str, str]:
        d = summarize_workflow_run(run)
        detail_parts: list[str] = []
        if d.run_error:
            detail_parts.append(f"Run: {format_diagnostic_preview(d.run_error, max_len=400)}")
        if d.failed_node_error_short:
            detail_parts.append(f"Knoten: {d.failed_node_error_short}")
        return {
            "headline": d.headline,
            "summary": d.summary,
            "detail": " · ".join(detail_parts) if detail_parts else "—",
            "runErrorFull": (d.run_error or "").strip(),
            "failedNodeId": (d.failed_node_id or "").strip(),
            "failedNodeType": (d.failed_node_type or "").strip(),
            "failedNodeErrorFull": (d.failed_node_error or "").strip(),
        }

    def node_run_rows(self, run: WorkflowRun) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for nr in run.node_runs:
            rows.append(
                {
                    "nodeRunId": nr.node_run_id,
                    "nodeId": nr.node_id,
                    "nodeType": nr.node_type,
                    "status": nr.status.value,
                    "started": nr.started_at.isoformat() if nr.started_at else "",
                    "finished": nr.finished_at.isoformat() if nr.finished_at else "",
                    "retryCount": int(nr.retry_count),
                    "errorPreview": format_diagnostic_preview(nr.error_message, max_len=160),
                }
            )
        return rows

    def json_preview(self, payload: dict[str, Any] | None, *, limit: int = 4000) -> str:
        if payload is None:
            return ""
        try:
            text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
        except (TypeError, ValueError):
            return ""
        if len(text) > limit:
            return text[: limit - 1] + "…"
        return text
