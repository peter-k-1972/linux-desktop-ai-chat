"""
Ableitung einer kompakten Run-Diagnose aus vorhandenen Run-/NodeRun-Daten (O2).

Keine Persistenz, keine Engine — nur lesbare Zusammenfassung für die UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.workflows.models.run import WorkflowRun
from app.workflows.status import NodeRunStatus, WorkflowRunStatus

# Anzeige-Kürzung; Volltext bleibt in Rohfeldern / Tooltips.
_SHORT_ERR_LEN = 240


def format_diagnostic_preview(msg: Optional[str], max_len: int = 200) -> str:
    """Einzeilige Kurzfassung für die Diagnose-Zeile in der UI."""
    s = _short_text(msg, max_len)
    return s if s else "—"


def _short_text(msg: Optional[str], max_len: int = _SHORT_ERR_LEN) -> str:
    if msg is None:
        return ""
    s = str(msg).strip()
    if not s:
        return ""
    one_line = " ".join(s.split())
    if len(one_line) <= max_len:
        return one_line
    return one_line[: max_len - 1] + "…"


@dataclass(frozen=True)
class WorkflowRunDiagnostics:
    headline: str
    summary: str
    run_error: Optional[str]
    failed_node_id: Optional[str]
    failed_node_type: Optional[str]
    failed_node_error: Optional[str]
    failed_node_error_short: Optional[str]
    is_completed: bool
    is_cancelled: bool
    is_failed: bool
    is_pending_or_running: bool


def _first_failed_node_run(run: WorkflowRun):
    for nr in run.node_runs:
        if nr.status == NodeRunStatus.FAILED:
            return nr
    return None


def summarize_workflow_run(run: WorkflowRun) -> WorkflowRunDiagnostics:
    """
    Leitet Headline und Kurztext aus Status, Run-Fehler und erstem FAILED-NodeRun ab.

    Priorität bei FAILED: erster NodeRun mit Status FAILED; sonst Run.error_message.
    """
    st = run.status
    is_completed = st == WorkflowRunStatus.COMPLETED
    is_cancelled = st == WorkflowRunStatus.CANCELLED
    is_failed = st == WorkflowRunStatus.FAILED
    is_pending_or_running = st in (WorkflowRunStatus.PENDING, WorkflowRunStatus.RUNNING)

    run_err = (run.error_message or "").strip() or None

    if is_completed:
        return WorkflowRunDiagnostics(
            headline="Erfolgreich abgeschlossen",
            summary="Der Workflow-Run ist mit Status „completed“ beendet worden.",
            run_error=None,
            failed_node_id=None,
            failed_node_type=None,
            failed_node_error=None,
            failed_node_error_short=None,
            is_completed=True,
            is_cancelled=False,
            is_failed=False,
            is_pending_or_running=False,
        )

    if is_cancelled:
        return WorkflowRunDiagnostics(
            headline="Abgebrochen",
            summary="Der Run wurde abgebrochen (cancelled).",
            run_error=run_err,
            failed_node_id=None,
            failed_node_type=None,
            failed_node_error=None,
            failed_node_error_short=None,
            is_completed=False,
            is_cancelled=True,
            is_failed=False,
            is_pending_or_running=False,
        )

    if is_pending_or_running:
        label = "Ausstehend" if st == WorkflowRunStatus.PENDING else "Läuft"
        return WorkflowRunDiagnostics(
            headline=label,
            summary=f"Status des Runs: „{st.value}“.",
            run_error=run_err,
            failed_node_id=None,
            failed_node_type=None,
            failed_node_error=None,
            failed_node_error_short=None,
            is_completed=False,
            is_cancelled=False,
            is_failed=False,
            is_pending_or_running=True,
        )

    if is_failed:
        fn = _first_failed_node_run(run)
        fn_err_raw = (fn.error_message or "").strip() if fn else None
        fn_err_short = _short_text(fn_err_raw) if fn_err_raw else None
        if fn is not None:
            headline = f"Fehlgeschlagen bei Knoten „{fn.node_id}“"
            summary = (
                f"Erster fehlgeschlagener Knoten: {fn.node_id} ({fn.node_type}). "
                "Details siehe Kurzfehler unten und Register „Fehler“."
            )
            return WorkflowRunDiagnostics(
                headline=headline,
                summary=summary,
                run_error=run_err,
                failed_node_id=fn.node_id,
                failed_node_type=fn.node_type,
                failed_node_error=fn_err_raw,
                failed_node_error_short=fn_err_short,
                is_completed=False,
                is_cancelled=False,
                is_failed=True,
                is_pending_or_running=False,
            )
        if run_err:
            return WorkflowRunDiagnostics(
                headline="Run fehlgeschlagen",
                summary=(
                    "Kein Knoten mit Status „failed“ in den gespeicherten NodeRuns — "
                    "Run-Fehlermeldung siehe unten (Run-Ebene)."
                ),
                run_error=run_err,
                failed_node_id=None,
                failed_node_type=None,
                failed_node_error=None,
                failed_node_error_short=None,
                is_completed=False,
                is_cancelled=False,
                is_failed=True,
                is_pending_or_running=False,
            )
        return WorkflowRunDiagnostics(
            headline="Run fehlgeschlagen",
            summary=(
                "Run fehlgeschlagen ohne gespeicherten Knotenfehler und ohne Run-Fehlermeldung "
                "(nur Status)."
            ),
            run_error=None,
            failed_node_id=None,
            failed_node_type=None,
            failed_node_error=None,
            failed_node_error_short=None,
            is_completed=False,
            is_cancelled=False,
            is_failed=True,
            is_pending_or_running=False,
        )

    return WorkflowRunDiagnostics(
        headline=f"Status: {st.value}",
        summary=f"Unbekannter oder seltener Run-Status: „{st.value}“.",
        run_error=run_err,
        failed_node_id=None,
        failed_node_type=None,
        failed_node_error=None,
        failed_node_error_short=None,
        is_completed=False,
        is_cancelled=False,
        is_failed=is_failed,
        is_pending_or_running=False,
    )
