"""Next-Run-Berechnung und Regel-V1 (UTC, optionales Intervall)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

MIN_REPEAT_INTERVAL_SECONDS = 60


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_utc_iso(value: str) -> datetime:
    s = (value or "").strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_utc_iso(dt: datetime) -> str:
    aware = dt.astimezone(timezone.utc)
    return aware.isoformat()


def parse_rule_json(rule_json: str) -> Dict[str, Any]:
    raw = (rule_json or "").strip() or "{}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"rule_json ist kein gültiges JSON: {e}") from e
    if not isinstance(data, dict):
        raise ValueError("rule_json muss ein JSON-Objekt sein.")
    return data


def validate_rule_dict(rule: Dict[str, Any]) -> Optional[int]:
    """
    Prüft ``repeat_interval_seconds`` falls gesetzt.

    Returns:
        Intervall in Sekunden oder None (Einmal / nur next_run_at).
    """
    if "repeat_interval_seconds" not in rule:
        return None
    v = rule["repeat_interval_seconds"]
    if not isinstance(v, int) or isinstance(v, bool):
        raise ValueError("repeat_interval_seconds muss eine ganze Zahl sein.")
    if v < MIN_REPEAT_INTERVAL_SECONDS:
        raise ValueError(
            f"repeat_interval_seconds muss >= {MIN_REPEAT_INTERVAL_SECONDS} sein."
        )
    return v


def next_run_after_due_execution(
    *,
    due_at_utc: datetime,
    now_utc: datetime,
    repeat_interval_seconds: Optional[int],
) -> Tuple[Optional[str], bool]:
    """
    Berechnet Folge-``next_run_at`` nach erfolgreichem Start eines fälligen Laufs.

    Returns:
        (next_run_at_iso oder None, disable_schedule)
        - Ohne Wiederholung: disable_schedule True, next None (Caller setzt enabled=0).
        - Mit Wiederholung: nächster Termin, disable False.
    """
    if repeat_interval_seconds is None:
        return None, True
    base = due_at_utc
    nxt = base + timedelta(seconds=repeat_interval_seconds)
    while nxt <= now_utc:
        nxt += timedelta(seconds=repeat_interval_seconds)
    return format_utc_iso(nxt), False
