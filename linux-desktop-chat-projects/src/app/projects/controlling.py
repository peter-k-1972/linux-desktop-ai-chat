"""Phase B: Anzeige-Helfer für Budget und Meilenstein-Kennzahlen (ohne Ist/Prozent)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from app.projects.milestones import MILESTONE_OPEN, milestone_status_label_de


def format_budget_display(amount: Optional[float], currency: Optional[str]) -> Optional[str]:
    """Eine Zeile Budget für UI; None wenn kein Betrag."""
    if amount is None:
        return None
    try:
        v = float(amount)
    except (TypeError, ValueError):
        return None
    if v < 0:
        return None
    s = f"{v:g}" if v == int(v) else f"{v:.2f}".rstrip("0").rstrip(".")
    cur = (currency or "").strip()
    return f"{s} {cur}" if cur else s


def format_effort_display(hours: Optional[float]) -> Optional[str]:
    if hours is None:
        return None
    try:
        v = float(hours)
    except (TypeError, ValueError):
        return None
    if v < 0:
        return None
    s = f"{v:g}" if v == int(v) else f"{v:.2f}".rstrip("0").rstrip(".")
    return f"{s} h"


def _parse_iso_date(s: str) -> Optional[date]:
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError, AttributeError):
        return None


def milestone_summary(milestones: List[Dict[str, Any]], today: Optional[date] = None) -> Dict[str, Any]:
    """
    Liefert verdichtete Meilenstein-Infos für Overview/Inspector.

    - next: dict | None — nächster offener Meilenstein nach Datum
    - open_count, overdue_count: int
    - upcoming_three: bis zu 3 offene Meilensteine sortiert nach Datum
    """
    t = today or date.today()
    open_ms: List[Dict[str, Any]] = []
    overdue = 0
    for m in milestones:
        st = (m.get("status") or MILESTONE_OPEN).strip().lower()
        if st != MILESTONE_OPEN:
            continue
        open_ms.append(m)
        td = m.get("target_date")
        if isinstance(td, str):
            d = _parse_iso_date(td)
            if d is not None and d < t:
                overdue += 1

    def sort_key(m: Dict[str, Any]) -> Tuple[date, int]:
        d = _parse_iso_date(str(m.get("target_date") or ""))
        mid = int(m.get("milestone_id") or 0)
        return (d or date.max, mid)

    open_ms.sort(key=sort_key)
    next_m = open_ms[0] if open_ms else None
    upcoming_three = open_ms[:3]

    return {
        "next_milestone": next_m,
        "open_count": len(open_ms),
        "overdue_count": overdue,
        "upcoming_three": upcoming_three,
    }


def format_next_milestone_line(m: Optional[Dict[str, Any]]) -> Optional[str]:
    if not m:
        return None
    name = (m.get("name") or "").strip() or "—"
    td = (m.get("target_date") or "").strip()
    st = milestone_status_label_de(m.get("status"))
    return f"{td} · {name} ({st})"


def format_milestone_compact_counts(open_count: int, overdue_count: int) -> str:
    return f"Offen: {open_count} · Überfällig: {overdue_count}"
