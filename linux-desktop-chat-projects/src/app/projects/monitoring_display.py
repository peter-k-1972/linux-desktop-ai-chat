"""
Kurztexte und Formatierung für Projekt-Monitoring (Phase C).

Keine Persistenz, keine Scores — nur Anzeige-Hilfen aus vorhandenen Aggregaten.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

_WORKFLOW_STATUS_DE: Dict[str, str] = {
    "pending": "ausstehend",
    "running": "läuft",
    "completed": "abgeschlossen",
    "failed": "fehlgeschlagen",
    "cancelled": "abgebrochen",
}


def format_timestamp_display(raw: Optional[str]) -> str:
    """Menschenlesbarer Zeitpunkt oder Platzhalter."""
    if raw is None or not str(raw).strip():
        return "—"
    s = str(raw).strip()
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return s


def workflow_run_status_label_de(status: Optional[str]) -> str:
    if status is None or not str(status).strip():
        return "—"
    key = str(status).strip().lower()
    return _WORKFLOW_STATUS_DE.get(key, key)


def knowledge_sources_line(source_count: int) -> str:
    n = int(source_count)
    if n <= 0:
        return "Knowledge: keine Quellen"
    return f"Knowledge: {n} Quelle(n)"


def failed_runs_hint(failed_30d: int) -> str:
    n = int(failed_30d)
    if n <= 0:
        return "Fehler-Runs (30 Tage): keine"
    return f"Fehler-Runs (30 Tage): {n}"


def monitoring_overview_lines(snapshot: Dict[str, Any]) -> list[str]:
    """Kompakte Zeilen für UI-Blöcke (Übersicht/Inspector)."""
    last_act = format_timestamp_display(snapshot.get("last_activity_at"))
    m7 = int(snapshot.get("message_count_7d") or 0)
    m30 = int(snapshot.get("message_count_30d") or 0)
    ch30 = int(snapshot.get("active_chats_30d") or 0)
    wr_at = format_timestamp_display(snapshot.get("last_workflow_run_at"))
    wr_st = workflow_run_status_label_de(snapshot.get("last_workflow_run_status"))
    fail_hint = failed_runs_hint(int(snapshot.get("failed_workflow_runs_30d") or 0))
    know = knowledge_sources_line(int(snapshot.get("source_count") or 0))
    return [
        f"Letzte Aktivität (Chat): {last_act}",
        f"Nachrichten: {m7} (7 Tage) · {m30} (30 Tage)",
        f"Aktive Chats (30 Tage): {ch30}",
        f"Letzter Workflow-Run: {wr_at} ({wr_st})",
        fail_hint,
        know,
    ]
