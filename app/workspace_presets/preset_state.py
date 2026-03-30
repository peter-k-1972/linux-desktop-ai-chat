"""
Workspace Preset — persistierter Produktzustand (QSettings, Slice 3).

Kein Overlay-Code. Fail-closed bei unbekannten oder ungültigen gespeicherten IDs.
"""

from __future__ import annotations

import logging

from app.workspace_presets.preset_models import PresetReleaseStatus
from app.core.startup_contract import (
    product_qsettings,
    write_preferred_gui_id_to_qsettings,
    write_product_theme_id_to_qsettings,
)
from app.workspace_presets.preset_registry import get_default_workspace_preset_id, get_workspace_preset
from app.workspace_presets.preset_validation import validate_workspace_preset

logger = logging.getLogger(__name__)

_QS_KEY_ACTIVE_PRESET = "active_workspace_preset_id"
_QS_KEY_START_DOMAIN = "workspace_preset_preferred_start_domain"
_QS_KEY_CONTEXT_PROFILE = "workspace_preset_context_profile"
_QS_KEY_OVERLAY_MODE = "workspace_preset_overlay_mode"
_QS_KEY_FULL_EFFECT_PENDING = "workspace_preset_full_effect_pending_restart"


def _qs():
    return product_qsettings()


def _coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ("true", "1", "yes", "on")


def read_full_effect_pending_restart() -> bool:
    """Persistierter Marker: vollständige Preset-Wirkung ausstehend (Relaunch/Follow-up)."""
    try:
        return _coerce_bool(_qs().value(_QS_KEY_FULL_EFFECT_PENDING, False))
    except Exception:
        return False


def write_full_effect_pending_restart(value: bool) -> None:
    qs = _qs()
    qs.setValue(_QS_KEY_FULL_EFFECT_PENDING, bool(value))
    qs.sync()


def read_raw_active_workspace_preset_id_from_storage() -> str:
    """Roher QSettings-Wert (kann leer/ungültig sein)."""
    try:
        raw = _qs().value(_QS_KEY_ACTIVE_PRESET, "")
        return (str(raw) if raw is not None else "").strip()
    except Exception:
        return ""


def _is_usable_preset_id(preset_id: str) -> bool:
    if not preset_id:
        return False
    try:
        p = get_workspace_preset(preset_id)
    except KeyError:
        return False
    if p.release_status == PresetReleaseStatus.DEPRECATED:
        return False
    if p.release_status != PresetReleaseStatus.APPROVED:
        return False
    if validate_workspace_preset(p):
        return False
    return True


def resolve_valid_active_workspace_preset_id() -> str:
    """
    Liest Speicher, validiert; bei Fehler Fallback auf Registry-Default und Korrektur der Speicherung.
    """
    raw = read_raw_active_workspace_preset_id_from_storage()
    default_id = get_default_workspace_preset_id()
    if not raw:
        return default_id
    if not _is_usable_preset_id(raw):
        logger.warning("Invalid or non-approved stored workspace preset %r; reverting to %s", raw, default_id)
        write_active_workspace_preset_bundle_to_storage(default_id)
        return default_id
    return raw


def write_active_workspace_preset_bundle_to_storage(
    preset_id: str,
    *,
    start_domain_override: str | None = None,
    sync_preferred_gui: bool = True,
    sync_preferred_theme: bool = True,
    persist_theme_from_preset: bool = True,
) -> None:
    """
    Persistiert aktives Preset und begleitende deklarative Zielwerte (Slice 3).

    ``preset_id`` muss strukturell gültig und ``approved`` sein — Aufrufer prüft (Aktivierungsservice).

    Slice 5: optional ``start_domain_override`` (z. B. Nav-Fallback bei Partial Activation).
    ``sync_preferred_gui`` / ``sync_preferred_theme`` steuern, ob ``preferred_gui`` bzw. ``theme_id``
    mitgeschrieben werden (z. B. wenn CLI/Env beim Start höhere Priorität hat).
    """
    p = get_workspace_preset(preset_id)
    domain_val = (start_domain_override or "").strip() or p.start_domain
    qs = _qs()
    qs.setValue(_QS_KEY_ACTIVE_PRESET, p.preset_id)
    qs.setValue(_QS_KEY_START_DOMAIN, domain_val)
    qs.setValue(_QS_KEY_CONTEXT_PROFILE, p.context_profile)
    qs.setValue(_QS_KEY_OVERLAY_MODE, p.overlay_mode)
    qs.sync()
    if sync_preferred_gui:
        write_preferred_gui_id_to_qsettings(p.gui_id)
    if sync_preferred_theme and persist_theme_from_preset:
        write_product_theme_id_to_qsettings(p.theme_id)


def read_preferred_start_domain_from_storage() -> str | None:
    try:
        raw = _qs().value(_QS_KEY_START_DOMAIN, "")
        s = (str(raw) if raw is not None else "").strip()
        return s or None
    except Exception:
        return None


def read_declarative_context_profile_from_storage() -> str | None:
    try:
        raw = _qs().value(_QS_KEY_CONTEXT_PROFILE, "")
        s = (str(raw) if raw is not None else "").strip()
        return s or None
    except Exception:
        return None


def read_declarative_overlay_mode_from_storage() -> str | None:
    try:
        raw = _qs().value(_QS_KEY_OVERLAY_MODE, "")
        s = (str(raw) if raw is not None else "").strip()
        return s or None
    except Exception:
        return None


def clear_active_workspace_preset_storage() -> None:
    """
    Entfernt Preset-Zustand aus QSettings und setzt Bundle auf Registry-Default.

    Für Tests und explizites „Zurücksetzen“ (Slice 3).
    """
    default_id = get_default_workspace_preset_id()
    write_active_workspace_preset_bundle_to_storage(default_id)
