"""
Chat-Integration für den Project Butler: Trigger-Heuristik, Workspace-Auflösung, Antwortformat.

Keine Chat-Pipeline-Architektur — nur Hilfsfunktionen für den Presenter.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Explizite Chat-Trigger (Substring, case-insensitive), unabhängig von Butler-interner Workflow-Klassifikation.
CHAT_BUTLER_TRIGGER_KEYWORDS: frozenset[str] = frozenset(
    {
        "fix",
        "bug",
        "refactor",
        "analysiere",
        "analyse",
        "bewerte",
        "erkläre",
        "erklaere",
        "context",
        "debug",
        "warum",
    }
)

_BUTLER_PREFIX = "/butler"


def is_chat_butler_disabled() -> bool:
    return os.environ.get("LINUX_DESKTOP_CHAT_DISABLE_BUTLER", "").strip() in ("1", "true", "yes", "on")


def should_activate_butler_for_chat_message(text: str) -> Tuple[bool, str]:
    """
    Liefert (True, anfrage_fuer_butler) wenn der Chat den Butler ausführen soll.

    - Nachricht beginnt mit ``/butler`` (optional Leerzeichen): immer aktiv, Präfix wird entfernt.
    - Sonst: mindestens ein Schlüsselwort aus ``CHAT_BUTLER_TRIGGER_KEYWORDS`` als Substring in ``text.lower()``.
    """
    if is_chat_butler_disabled():
        return False, (text or "").strip()

    raw = (text or "").strip()
    if not raw:
        return False, raw

    lower = raw.lower()
    if lower.startswith(_BUTLER_PREFIX):
        rest = raw[len(_BUTLER_PREFIX) :].lstrip()
        logger.info("chat_butler: Trigger via %s", _BUTLER_PREFIX)
        return True, rest if rest else raw

    for kw in CHAT_BUTLER_TRIGGER_KEYWORDS:
        if kw in lower:
            logger.info("chat_butler: Trigger via Schlüsselwort %r", kw)
            return True, raw

    return False, raw


def resolve_workspace_root_for_butler(chat_id: int) -> Optional[str]:
    """
    Leitet workspace_root aus Chat-/Projekt-Dateizuordnungen ab (erstes Verzeichnis oder Elternpfad einer Datei).
    """
    try:
        from app.services.infrastructure import get_infrastructure

        roots = get_infrastructure().database.list_workspace_roots_for_chat(chat_id)
    except Exception:
        logger.debug("chat_butler: workspace_root konnte nicht ermittelt werden", exc_info=True)
        return None

    import os as _os

    for path, ftype in roots or []:
        p = str(path or "").strip()
        if not p:
            continue
        t = (ftype or "").lower()
        if t == "directory" or _os.path.isdir(p):
            return p
        if _os.path.isfile(p):
            return str(Path(p).resolve().parent)
    return None


def build_butler_optional_context(chat_id: int) -> Dict[str, Any]:
    """
    Nur vorhandene, sinnvolle Werte für ``ProjectButlerService.handle(…, optional_context=…)``.

    - ``chat_id``: immer (für nachgelagerte Workflow-/Kontext-Schritte).
    - ``workspace_root``: nur wenn aus Chat-Dateizuordnung ableitbar.
    """
    out: Dict[str, Any] = {"chat_id": int(chat_id)}
    wr = resolve_workspace_root_for_butler(chat_id)
    if wr:
        out["workspace_root"] = wr
    return out


def run_project_butler_sync(user_request: str, optional_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Synchrone Butler-Ausführung (für asyncio.to_thread). Eigene Funktion zum Testen (monkeypatch)."""
    from app.services.project_butler_service import ProjectButlerService
    from app.services.workflow_service import get_workflow_service

    return ProjectButlerService(get_workflow_service()).handle(user_request, optional_context=optional_context)


def format_butler_result_as_chat_message(butler_out: Dict[str, Any]) -> str:
    """Formatiert die Butler-Rückgabe als lesbare Chat-Antwort (plain text mit Abschnitten)."""
    lines: list[str] = ["Project Butler", ""]
    sel = butler_out.get("selected_workflow")
    reasoning = (butler_out.get("reasoning") or "").strip()
    res: Dict[str, Any] = dict(butler_out.get("result") or {})

    if sel is None:
        lines.append("Project Butler konnte keine passende Aufgabe erkennen.")
        if reasoning:
            lines.append("")
            lines.append(reasoning)
        return "\n".join(lines)

    wf = str(sel)
    if wf.startswith("workflow."):
        wf = wf[len("workflow.") :]
    lines.append(f"Workflow: {wf}")
    lines.append("")

    outcome = res.get("outcome")
    if outcome == "error":
        detail = res.get("detail", res)
        lines.append(f"Fehler: {detail}")
        return "\n".join(lines)

    if outcome != "workflow_finished":
        lines.append(str(res))
        return "\n".join(lines)

    status = res.get("status")
    if status is not None:
        lines.append(f"Status: {status}")
        lines.append("")

    fo = res.get("final_output")
    if isinstance(fo, dict):
        sections = [
            ("Analyse", fo.get("analysis")),
            ("Plan", fo.get("plan")),
            ("Review", fo.get("review")),
            ("Dokumentation", fo.get("documentation")),
        ]
        any_section = False
        for title, val in sections:
            if val is None:
                continue
            s = str(val).strip()
            if not s:
                continue
            any_section = True
            lines.append(title)
            lines.append(s)
            lines.append("")

        if "patch_applied" in fo:
            lines.append(f"Patch angewendet: {fo.get('patch_applied')}")
            lines.append("")

        tr = fo.get("test_results")
        if tr is not None and str(tr).strip():
            lines.append("Tests")
            lines.append(str(tr).strip())
            lines.append("")

        if not any_section:
            summ = str(fo.get("summary") or "").strip()
            if summ:
                lines.append(summ)
                lines.append("")
            # kompakte JSON-Zusammenfassung für Platzhalter-Workflows
            try:
                compact = {k: fo[k] for k in ("phase", "kind", "user_request") if k in fo}
                if compact:
                    lines.append(json.dumps(compact, ensure_ascii=False, indent=2))
            except Exception:
                pass
    elif fo is not None:
        lines.append(str(fo))

    return "\n".join(lines).rstrip()
