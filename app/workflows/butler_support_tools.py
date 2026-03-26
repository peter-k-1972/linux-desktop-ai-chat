"""Deterministische Hilfs-Callables für Butler-Phase-1-Workflows (ohne LLM)."""

from __future__ import annotations

from typing import Any, Dict

from app.pipelines.executors import StepResult


def butler_analyze_decide_document_phase1(context: Dict[str, Any]) -> StepResult:
    """
    Platzhalter: strukturiertes Ergebnis für Analyse/Dokumentations-Pfad.
    Später: echte Agenten-Knoten ergänzen, ohne die Butler-Schnittstelle zu ändern.
    """
    ur = str(context.get("user_request") or "").strip()
    out: Dict[str, Any] = {
        "phase": "analyze_decide_document",
        "kind": "phase1_placeholder",
        "summary": (
            "Phase-1: Anfrage wurde dem Workflow analyze_decide_document zugeordnet. "
            "Detaillierte Analyse/Entscheid/Dokumentation folgt in späteren Ausbaustufen."
        ),
        "user_request": ur,
    }
    oc = context.get("optional_context")
    if isinstance(oc, dict) and oc:
        out["optional_context_keys"] = sorted(oc.keys())
    return StepResult(success=True, output=out)


def butler_context_inspect_phase1(context: Dict[str, Any]) -> StepResult:
    """Platzhalter für Kontext-/Debug-Pfad (z. B. später Anbindung an ContextInspectionService)."""
    ur = str(context.get("user_request") or "").strip()
    out: Dict[str, Any] = {
        "phase": "context_inspect",
        "kind": "phase1_placeholder",
        "summary": (
            "Phase-1: Anfrage wurde dem Workflow context_inspect zugeordnet. "
            "Tiefe Kontextinspektion kann hier angebunden werden."
        ),
        "user_request": ur,
    }
    oc = context.get("optional_context")
    if isinstance(oc, dict) and oc:
        out["optional_context_keys"] = sorted(oc.keys())
    return StepResult(success=True, output=out)
