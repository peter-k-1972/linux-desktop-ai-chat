"""Projekt-Meilensteine (Phase B) – Statuswerte und Validierung."""

from __future__ import annotations

from typing import Final, Optional

from app.projects.lifecycle import normalize_optional_plan_date, normalize_optional_text

MILESTONE_OPEN: Final = "open"
MILESTONE_DONE: Final = "done"
MILESTONE_DEFERRED: Final = "deferred"

ALLOWED_MILESTONE_STATUSES: Final[frozenset[str]] = frozenset(
    {MILESTONE_OPEN, MILESTONE_DONE, MILESTONE_DEFERRED}
)

_STATUS_LABELS_DE: dict[str, str] = {
    MILESTONE_OPEN: "Offen",
    MILESTONE_DONE: "Erreicht",
    MILESTONE_DEFERRED: "Verschoben",
}


def milestone_status_label_de(value: Optional[str]) -> str:
    if not value:
        return _STATUS_LABELS_DE[MILESTONE_OPEN]
    k = str(value).strip().lower()
    return _STATUS_LABELS_DE.get(k, k)


def milestone_status_combo_entries() -> list[tuple[str, str]]:
    return [
        (_STATUS_LABELS_DE[MILESTONE_OPEN], MILESTONE_OPEN),
        (_STATUS_LABELS_DE[MILESTONE_DONE], MILESTONE_DONE),
        (_STATUS_LABELS_DE[MILESTONE_DEFERRED], MILESTONE_DEFERRED),
    ]


def validate_milestone_status(raw: str) -> str:
    s = str(raw).strip().lower()
    if s not in ALLOWED_MILESTONE_STATUSES:
        raise ValueError(f"Ungültiger Meilenstein-Status: {raw!r}")
    return s


def validate_milestone_name(raw: Optional[str]) -> str:
    n = normalize_optional_text(raw)
    if not n:
        raise ValueError("Meilenstein-Name darf nicht leer sein")
    return n


def validate_milestone_target_date(raw: Optional[str]) -> str:
    if raw is None or not str(raw).strip():
        raise ValueError("Meilenstein-Zieldatum erforderlich (YYYY-MM-DD)")
    return normalize_optional_plan_date(raw)
