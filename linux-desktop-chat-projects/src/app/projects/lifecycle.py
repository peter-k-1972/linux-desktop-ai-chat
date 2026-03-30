"""
Projekt-Lebenszyklus (Phase A) – erlaubte Werte, UI-Labels, Validierung.

Technisches Feld ``projects.status`` bleibt davon unabhängig.
"""

from __future__ import annotations

import re
from typing import Final, Optional

# Persistierte Werte (lowercase snake_case)
LIFECYCLE_PLANNED: Final = "planned"
LIFECYCLE_ACTIVE: Final = "active"
LIFECYCLE_ON_HOLD: Final = "on_hold"
LIFECYCLE_COMPLETED: Final = "completed"
LIFECYCLE_CANCELLED: Final = "cancelled"

ALLOWED_LIFECYCLE_STATUSES: Final[frozenset[str]] = frozenset(
    {
        LIFECYCLE_PLANNED,
        LIFECYCLE_ACTIVE,
        LIFECYCLE_ON_HOLD,
        LIFECYCLE_COMPLETED,
        LIFECYCLE_CANCELLED,
    }
)

DEFAULT_LIFECYCLE_STATUS: Final[str] = LIFECYCLE_ACTIVE

_LIFECYCLE_LABELS_DE: dict[str, str] = {
    LIFECYCLE_PLANNED: "Geplant",
    LIFECYCLE_ACTIVE: "Aktiv",
    LIFECYCLE_ON_HOLD: "Pausiert",
    LIFECYCLE_COMPLETED: "Abgeschlossen",
    LIFECYCLE_CANCELLED: "Storniert",
}

_PLAN_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def lifecycle_label_de(value: Optional[str]) -> str:
    """Anzeigetext für einen gespeicherten lifecycle_status."""
    if not value or not isinstance(value, str):
        return _LIFECYCLE_LABELS_DE.get(DEFAULT_LIFECYCLE_STATUS, DEFAULT_LIFECYCLE_STATUS)
    key = value.strip().lower()
    return _LIFECYCLE_LABELS_DE.get(key, key)


def lifecycle_combo_entries() -> list[tuple[str, str]]:
    """(UI-Label, persistierter Wert) für Comboboxen."""
    return [
        (_LIFECYCLE_LABELS_DE[LIFECYCLE_PLANNED], LIFECYCLE_PLANNED),
        (_LIFECYCLE_LABELS_DE[LIFECYCLE_ACTIVE], LIFECYCLE_ACTIVE),
        (_LIFECYCLE_LABELS_DE[LIFECYCLE_ON_HOLD], LIFECYCLE_ON_HOLD),
        (_LIFECYCLE_LABELS_DE[LIFECYCLE_COMPLETED], LIFECYCLE_COMPLETED),
        (_LIFECYCLE_LABELS_DE[LIFECYCLE_CANCELLED], LIFECYCLE_CANCELLED),
    ]


def validate_lifecycle_status(raw: str) -> str:
    """
    Prüft und normalisiert lifecycle_status.

    Raises:
        ValueError: bei unbekanntem oder leerem Wert.
    """
    if raw is None:
        raise ValueError("lifecycle_status fehlt")
    s = str(raw).strip().lower()
    if not s:
        raise ValueError("lifecycle_status darf nicht leer sein")
    if s not in ALLOWED_LIFECYCLE_STATUSES:
        raise ValueError(f"Ungültiger lifecycle_status: {raw!r}")
    return s


def normalize_optional_plan_date(raw: Optional[str]) -> Optional[str]:
    """
    Akzeptiert None oder Leerstring → None.
    Sonst muss der Wert exakt YYYY-MM-DD sein.

    Raises:
        ValueError: bei ungültigem Format oder ungültigem Kalenderdatum.
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if not _PLAN_DATE_RE.match(s):
        raise ValueError(f"Plan-Datum muss YYYY-MM-DD sein, nicht {raw!r}")
    y_str, m_str, d_str = s.split("-")
    y, m, d = int(y_str), int(m_str), int(d_str)
    if m < 1 or m > 12 or d < 1 or d > 31:
        raise ValueError(f"Ungültiges Datum: {raw!r}")
    # Kalenderprüfung (Schaltjahre)
    from datetime import date

    try:
        date(y, m, d)
    except ValueError as e:
        raise ValueError(f"Ungültiges Datum: {raw!r}") from e
    return s


def normalize_optional_text(raw: Optional[str]) -> Optional[str]:
    """Leerstring nach strip → None; sonst strip."""
    if raw is None:
        return None
    s = str(raw).strip()
    return s if s else None
