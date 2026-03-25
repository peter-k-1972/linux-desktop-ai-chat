"""
Einheitliche erlaubte Nav-Menge für alle GUI-Konsumenten (Sidebar, Breadcrumbs, Subnav, …).

Quelle: ``collect_active_navigation_entry_ids(get_feature_registry())``.
Keine zweite Filterdefinition — nur Delegation zu ``app.features.nav_binding``.
"""

from __future__ import annotations

from typing import Optional

from app.core.navigation.navigation_registry import get_all_entries
from app.features.feature_registry import get_feature_registry
from app.features.nav_binding import collect_active_navigation_entry_ids

_FALLBACK_BREADCRUMB_TITLE = "App"


def allowed_navigation_entry_ids() -> Optional[frozenset[str]]:
    """``None`` = keine Registry gesetzt → ungefiltert (Legacy/Tests)."""
    fr = get_feature_registry()
    if fr is None:
        return None
    return collect_active_navigation_entry_ids(fr)


def is_nav_entry_allowed(entry_id: str) -> bool:
    allowed = allowed_navigation_entry_ids()
    return allowed is None or entry_id in allowed


def is_area_visible_in_nav(area_id: str) -> bool:
    """True, wenn mindestens ein erlaubter Registry-Eintrag zu ``area_id`` gehört."""
    allowed = allowed_navigation_entry_ids()
    if allowed is None:
        return True
    entries = get_all_entries()
    for eid in allowed:
        ent = entries.get(eid)
        if ent is not None and ent.area == area_id:
            return True
    return False


def neutral_breadcrumb_fallback_title() -> str:
    """Anzeigetext, wenn der Kontext auf inaktive Nav-Ziele zeigt (fail-soft)."""
    return _FALLBACK_BREADCRUMB_TITLE
