"""
Fingerprint V1 für Incidents — deterministisch, ohne Heuristik.

Bildung (siehe Modul-Docstring unten): stabile Felder aus WorkflowRun,
konsistent zur O2-Diagnose (erster FAILED NodeRun, sonst Run-Fehler).

app/workflows/diagnostics.py wird nicht importiert, damit die Schichtung
core/audit → workflows vermieden wird; die Logik entspricht _first_failed_node_run.
"""

from __future__ import annotations

import hashlib
from typing import Optional, Tuple

from app.workflows.models.run import WorkflowRun
from app.workflows.status import NodeRunStatus, WorkflowRunStatus

# Unit separator — unlikely in IDs
_SEP = "\x1f"


def _normalize_error_message(msg: Optional[str], max_len: int = 400) -> str:
    if msg is None:
        return ""
    s = " ".join(str(msg).strip().split())
    if len(s) <= max_len:
        return s
    return s[:max_len]


def _first_failed_node_run(run: WorkflowRun):
    for nr in run.node_runs:
        if nr.status == NodeRunStatus.FAILED:
            return nr
    return None


def failure_fingerprint_inputs(run: WorkflowRun) -> Tuple[str, Optional[str], Optional[str], str]:
    """
    Liefert (workflow_id, failed_node_id, failed_node_type, normalized_error) für Anzeige
    und Fingerprint. Entspricht der O2-Priorität: erster FAILED-Knoten, sonst Run-Fehler.
    """
    wid = (run.workflow_id or "").strip()
    fn = _first_failed_node_run(run)
    if fn is not None:
        nid = (fn.node_id or "").strip() or None
        ntype = (fn.node_type or "").strip() or None
        err = _normalize_error_message(fn.error_message)
        return wid, nid, ntype, err
    run_err = _normalize_error_message(run.error_message)
    return wid, None, None, run_err


def compute_incident_fingerprint(run: WorkflowRun) -> str:
    """
    Fingerprint V1 (deterministisch):

    1. ``workflow_id`` — aus dem Run, getrimmt.
    2. ``failed_node_id`` — ID des ersten NodeRuns mit Status FAILED; leerer String,
       wenn kein solcher Knoten existiert (Run-Level-Fehler).
    3. ``failed_node_type`` — ``node_type`` desselben Knotens; leerer String wenn keiner.
    4. ``normalized_error`` — primäre Fehlermeldung: zuerst vom ersten FAILED-Knoten,
       sonst ``run.error_message``; Whitespace zu einfachen Spaces normalisiert,
       maximal 400 Zeichen.

    SHA-256 über die UTF-8-Kodierung von
    ``workflow_id + SEP + failed_node_id + SEP + failed_node_type + SEP + normalized_error``.

    Gleiche Ursachenklasse (Workflow + Knotenposition + gleicher gekürzter Fehltext)
    → gleicher Fingerprint → idempotentes Incident-Update (occurrence_count).
    """
    if run.status != WorkflowRunStatus.FAILED:
        raise ValueError("Fingerprint nur für terminal FAILED Runs definiert.")
    wid, nid, ntype, err = failure_fingerprint_inputs(run)
    nid_s = nid or ""
    ntype_s = ntype or ""
    canonical = _SEP.join((wid, nid_s, ntype_s, err))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def diagnostic_code_for_run(run: WorkflowRun) -> Optional[str]:
    """Kurzcode für Anzeige/Persistenz: gekürzter normalisierter Fehltext (max. 120)."""
    _, _, _, err = failure_fingerprint_inputs(run)
    if not err:
        return None
    return err[:120] if len(err) > 120 else err
