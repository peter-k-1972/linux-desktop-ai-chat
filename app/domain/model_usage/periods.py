"""
Deterministische UTC-Perioden für Aggregationen.

Woche: ISO-Woche, Start Montag 00:00 UTC (analog ISO 8601).
Total: fester Anker ``1970-01-01T00:00:00+00:00`` für ``period_start``.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def period_starts(at: datetime | None = None) -> Dict[str, datetime]:
    t = at if at is not None else utc_now()
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    else:
        t = t.astimezone(timezone.utc)

    hour_start = t.replace(minute=0, second=0, microsecond=0)
    day_start = t.replace(hour=0, minute=0, second=0, microsecond=0)
    wd = t.weekday()
    week_start = (day_start - timedelta(days=wd)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    month_start = t.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_anchor = datetime(1970, 1, 1, tzinfo=timezone.utc)

    return {
        "hour": hour_start,
        "day": day_start,
        "week": week_start,
        "month": month_start,
        "total": total_anchor,
    }
