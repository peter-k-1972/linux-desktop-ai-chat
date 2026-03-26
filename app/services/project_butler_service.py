"""
Project Butler — schlanke Orchestrierung: Anfrage klassifizieren, Workflow wählen, ausführen.

Logische Agenten-ID (Profil): agent.project.butler
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple

from app.services.workflow_service import WorkflowNotFoundError, WorkflowService, WorkflowValidationError
from app.workflows.dev_assist_definition import WORKFLOW_ID as WORKFLOW_ID_DEV_ASSIST
from app.workflows.butler_support_definitions import (
    WORKFLOW_ID_ANALYZE_DECIDE_DOCUMENT,
    WORKFLOW_ID_CONTEXT_INSPECT,
)
from app.workflows.models.run import WorkflowRun
from app.workflows.status import WorkflowRunStatus

logger = logging.getLogger(__name__)

AGENT_ID_PROJECT_BUTLER = "agent.project.butler"


@dataclass(frozen=True)
class ButlerClassificationRule:
    """Eine Regel: erste passende Regel in der Liste gewinnt (Reihenfolge = Priorität)."""

    workflow_id: str
    keywords: frozenset[str]
    label: str


# Erweiterung: neue Einträge ans Ende oder neue Liste an classify_user_request(rules=...) übergeben.
DEFAULT_BUTLER_RULES: Tuple[ButlerClassificationRule, ...] = (
    ButlerClassificationRule(
        WORKFLOW_ID_DEV_ASSIST,
        frozenset(
            {
                "fix",
                "bug",
                "bugfix",
                "ändern",
                "aendern",
                "refactor",
                "patch",
                "implement",
                "implementieren",
                "code",
                "hotfix",
            }
        ),
        "Schlüsselwörter für Codeänderung, Bugfix oder Implementierung",
    ),
    ButlerClassificationRule(
        WORKFLOW_ID_ANALYZE_DECIDE_DOCUMENT,
        frozenset(
            {
                "analysiere",
                "analyse",
                "erkläre",
                "erklaere",
                "bewerte",
                "architektur",
                "einordnen",
                "dokumentier",
                "document",
                "explain",
                "analyze",
                "evaluate",
                "architecture",
            }
        ),
        "Schlüsselwörter für Analyse, Erklärung, Bewertung oder Architektur",
    ),
    ButlerClassificationRule(
        WORKFLOW_ID_CONTEXT_INSPECT,
        frozenset(
            {
                "context",
                "kontext",
                "warum",
                "replay",
                "debug",
                "nachvollziehen",
                "trace",
                "inspect",
                "why",
            }
        ),
        "Schlüsselwörter für Kontext, Debug oder Nachvollziehbarkeit",
    ),
)


def classify_user_request(
    text: str,
    rules: Sequence[ButlerClassificationRule] = DEFAULT_BUTLER_RULES,
) -> Tuple[Optional[str], str]:
    """
    Liefert (workflow_id oder None, nachvollziehbare Begründung).
    Vergleich case-insensitive; Teilstrings (Substring-Match).
    """
    raw = (text or "").strip()
    if not raw:
        return None, "Leere Anfrage — kein Workflow gewählt."

    t = raw.lower()
    for rule in rules:
        hits = sorted({k for k in rule.keywords if k in t})
        if hits:
            return rule.workflow_id, f"Treffer: {', '.join(hits)} — {rule.label}."
    return None, "Keine bekannten Schlüsselwörter — bitte Anfrage präzisieren (z. B. Bugfix, Analyse, Kontext)."


def build_workflow_initial_input(
    workflow_id: str,
    user_request: str,
    optional_context: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Mappt Butler-Eingabe auf das erwartete initial_input des Ziel-Workflows."""
    oc = dict(optional_context or {})
    if workflow_id == WORKFLOW_ID_DEV_ASSIST:
        return {**oc, "problem_description": user_request}
    return {
        **oc,
        "user_request": user_request,
        "optional_context": dict(optional_context or {}),
    }


def _run_summary(run: WorkflowRun) -> Dict[str, Any]:
    st = run.status
    sv = st.value if isinstance(st, WorkflowRunStatus) else str(st)
    return {
        "run_id": run.run_id,
        "workflow_id": run.workflow_id,
        "status": sv,
        "final_output": run.final_output,
        "error_message": run.error_message,
    }


class ProjectButlerService:
    """Orchestrierung über WorkflowService.start_run — kein Bypass der Engine."""

    def __init__(self, workflow_service: WorkflowService) -> None:
        self._workflow = workflow_service

    def handle(
        self,
        user_request: str,
        optional_context: Optional[Dict[str, Any]] = None,
        *,
        rules: Sequence[ButlerClassificationRule] = DEFAULT_BUTLER_RULES,
    ) -> Dict[str, Any]:
        """
        Eingabe wie ``{"user_request": "...", "optional_context": {...}}`` — hier als Parameter.

        Rückgabe: selected_workflow, reasoning, result (Zusammenfassung oder Fehlerobjekt).
        """
        wf_id, reasoning = classify_user_request(user_request, rules=rules)
        logger.info("project_butler: Anfrage (Kürzel) %r -> Workflow %s", (user_request or "")[:120], wf_id)

        if wf_id is None:
            out = {
                "selected_workflow": None,
                "reasoning": reasoning,
                "result": {
                    "outcome": "no_workflow_matched",
                    "detail": reasoning,
                },
            }
            logger.info("project_butler: kein Workflow gewählt — %s", reasoning)
            return out

        initial = build_workflow_initial_input(wf_id, user_request, optional_context)
        try:
            run = self._workflow.start_run(wf_id, initial)
        except WorkflowNotFoundError as e:
            msg = f"Workflow nicht registriert: {e}"
            logger.warning("project_butler: %s", msg)
            return {
                "selected_workflow": wf_id,
                "reasoning": reasoning,
                "result": {"outcome": "error", "error": "workflow_not_found", "detail": str(e)},
            }
        except WorkflowValidationError as e:
            msg = f"Workflow ungültig: {e}"
            logger.warning("project_butler: %s", msg)
            return {
                "selected_workflow": wf_id,
                "reasoning": reasoning,
                "result": {"outcome": "error", "error": "workflow_invalid", "detail": str(e)},
            }
        except Exception as e:
            logger.exception("project_butler: unerwarteter Fehler bei start_run")
            return {
                "selected_workflow": wf_id,
                "reasoning": reasoning,
                "result": {"outcome": "error", "error": "unexpected", "detail": str(e)},
            }

        summary = _run_summary(run)
        logger.info(
            "project_butler: Run %s workflow=%s status=%s",
            summary.get("run_id"),
            summary.get("workflow_id"),
            summary.get("status"),
        )
        return {
            "selected_workflow": wf_id,
            "reasoning": reasoning,
            "result": {"outcome": "workflow_finished", **_run_summary(run)},
        }
