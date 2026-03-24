"""
Strukturelle Preset-Validierung (Slice 1 — keine Aktivierung / kein Relaunch).
"""

from __future__ import annotations

from app.core.config.builtin_theme_ids import BUILTIN_THEME_IDS
from app.core.navigation.navigation_registry import get_entry
from app.gui_registry import list_registered_gui_ids

from app.workspace_presets.preset_models import (
    CONTEXT_PROFILES,
    LAYOUT_MODES,
    OVERLAY_MODES,
    RESCUE_BIAS,
    PresetReleaseStatus,
    WorkspacePreset,
)


def theme_id_valid_for_workspace_preset_registry(theme_id: str) -> bool:
    """
    Slice 1 structural check aligned with runtime compatibility:

    - Built-in theme IDs are always allowed.
    - Other IDs count if they appear in the active theme registry (same idea as
      :func:`app.gui.themes.theme_id_utils.is_registered_theme_id`).

    If the registry cannot be queried (e.g. very early import), built-ins only.
    """
    tid = (theme_id or "").strip()
    if not tid:
        return False
    if tid in BUILTIN_THEME_IDS:
        return True
    try:
        from app.gui.themes.theme_id_utils import is_registered_theme_id

        return bool(is_registered_theme_id(tid))
    except Exception:
        return False


def validate_workspace_preset(preset: WorkspacePreset) -> list[str]:
    """
    Statische / strukturelle Prüfung eines Presets.

    Returns:
        Liste von Fehlermeldungen; leer = gültig.
    """
    errors: list[str] = []

    if not (preset.preset_id or "").strip():
        errors.append("preset_id is empty")

    if not (preset.display_name or "").strip():
        errors.append("display_name is empty")

    if not (preset.description or "").strip():
        errors.append("description is empty")

    if not (preset.gui_id or "").strip():
        errors.append("gui_id is empty")
    elif preset.gui_id not in list_registered_gui_ids():
        errors.append(f"unknown gui_id: {preset.gui_id!r}")

    if not (preset.theme_id or "").strip():
        errors.append("theme_id is empty")
    elif not theme_id_valid_for_workspace_preset_registry(preset.theme_id):
        errors.append(
            f"theme_id {preset.theme_id!r} is not a built-in or registered product theme "
            f"(see theme_id_valid_for_workspace_preset_registry)"
        )

    if not (preset.start_domain or "").strip():
        errors.append("start_domain is empty")
    elif get_entry(preset.start_domain) is None:
        errors.append(f"unknown start_domain (nav entry id): {preset.start_domain!r}")

    if preset.layout_mode not in LAYOUT_MODES:
        errors.append(f"invalid layout_mode: {preset.layout_mode!r}")

    if preset.context_profile not in CONTEXT_PROFILES:
        errors.append(f"invalid context_profile: {preset.context_profile!r}")

    if preset.overlay_mode not in OVERLAY_MODES:
        errors.append(f"invalid overlay_mode: {preset.overlay_mode!r}")

    if preset.rescue_bias not in RESCUE_BIAS:
        errors.append(f"invalid rescue_bias: {preset.rescue_bias!r}")

    try:
        PresetReleaseStatus(preset.release_status)
    except ValueError:
        errors.append(f"invalid release_status: {preset.release_status!r}")

    if not preset.compatible_app_versions:
        errors.append("compatible_app_versions must be non-empty")

    return errors


def assert_registered_presets_valid(presets_by_id: dict[str, WorkspacePreset]) -> None:
    """Prüft Eindeutigkeit der IDs und strukturelle Gültigkeit jedes Eintrags."""
    seen: set[str] = set()
    for pid, preset in presets_by_id.items():
        if pid != preset.preset_id:
            raise ValueError(f"registry key {pid!r} != preset.preset_id {preset.preset_id!r}")
        if pid in seen:
            raise ValueError(f"duplicate preset_id in registry: {pid!r}")
        seen.add(pid)
        errs = validate_workspace_preset(preset)
        if errs:
            raise ValueError(f"preset {pid!r} invalid: " + "; ".join(errs))


def collect_all_validation_errors(presets_by_id: dict[str, WorkspacePreset]) -> list[str]:
    """Sammelt alle Validierungsfehler (inkl. Registry-Konsistenz), ohne sofort zu werfen."""
    out: list[str] = []
    keys = set(presets_by_id.keys())
    ids = {p.preset_id for p in presets_by_id.values()}
    if keys != ids:
        out.append(f"registry keys != preset_id set: keys={sorted(keys)!r} ids={sorted(ids)!r}")
    if len(keys) != len(presets_by_id):
        out.append("duplicate keys in presets_by_id")
    for pid, preset in presets_by_id.items():
        out.extend(f"{pid}: {e}" for e in validate_workspace_preset(preset))
    return out
