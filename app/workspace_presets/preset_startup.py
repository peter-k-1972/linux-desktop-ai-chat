"""
Workspace Preset — Produktstart (Slice 5).

Lädt den persistierten Arbeitsmodus, wendet sofortige Effekte auf Produktpräferenzen an
(ohne Safe Mode / ohne explizite CLI- oder Env-Overrides) und liefert die Start-Navigation.
"""

from __future__ import annotations

import logging
import os

from app.core.navigation.nav_areas import NavArea
from app.core.navigation.navigation_registry import get_entry
from app.workspace_presets.preset_activation import get_active_workspace_preset
from app.workspace_presets.preset_compatibility import (
    FALLBACK_START_DOMAIN_ID,
    build_workspace_preset_compatibility_report,
)
from app.core.startup_contract import argv_has_long_option
from app.workspace_presets.preset_restart_boundaries import (
    build_workspace_preset_boundary_report,
    safe_mode_runtime_active,
)
from app.workspace_presets.preset_state import (
    read_raw_active_workspace_preset_id_from_storage,
    resolve_valid_active_workspace_preset_id,
    write_full_effect_pending_restart,
)

logger = logging.getLogger(__name__)


def _gui_launch_explicitly_overridden(argv: list[str]) -> bool:
    if argv_has_long_option(argv, "--gui"):
        return True
    return bool((os.environ.get("LINUX_DESKTOP_CHAT_GUI") or "").strip())


def _theme_launch_explicitly_overridden(argv: list[str]) -> bool:
    if argv_has_long_option(argv, "--theme"):
        return True
    return bool((os.environ.get("LINUX_DESKTOP_CHAT_THEME") or "").strip())


def sync_workspace_preset_preferences_before_gui_resolution(argv: list[str]) -> None:
    """
    Vor ``resolve_active_gui_id``: Preset-Ziele in QSettings spiegeln, wenn der Nutzer
    GUI/Theme nicht per CLI/Env überschreibt und kein Safe-Mode-Laufzeitblock aktiv ist.

    Nur wenn ein ``active_workspace_preset_id`` gespeichert ist (kein stiller Default ohne Keys).
    """
    if safe_mode_runtime_active():
        logger.info("workspace preset launch sync skipped (safe mode runtime active)")
        return
    if not read_raw_active_workspace_preset_id_from_storage().strip():
        return

    gui_override = _gui_launch_explicitly_overridden(argv)
    theme_override = _theme_launch_explicitly_overridden(argv)
    if gui_override or theme_override:
        logger.info(
            "workspace preset launch sync: dimensional overrides active "
            "(gui_override=%s theme_override=%s) — bundle always; GUI/theme writes per dimension",
            gui_override,
            theme_override,
        )

    preset_id = resolve_valid_active_workspace_preset_id()
    preset = get_active_workspace_preset()
    compat = build_workspace_preset_compatibility_report(preset)
    if not compat.activation_allowed:
        logger.warning(
            "workspace preset launch sync skipped — gui not compatible for preset %r: %s",
            preset_id,
            "; ".join(compat.issues),
        )
        return

    from app.workspace_presets.preset_state import write_active_workspace_preset_bundle_to_storage

    sync_gui = not gui_override
    sync_theme = not theme_override
    write_active_workspace_preset_bundle_to_storage(
        preset_id,
        start_domain_override=compat.effective_start_domain if not compat.domain_ok else None,
        sync_preferred_gui=sync_gui,
        sync_preferred_theme=sync_theme,
        persist_theme_from_preset=bool(compat.theme_ok and sync_theme),
    )


def apply_workspace_preset_runtime_after_infrastructure(
    *,
    running_gui_id: str,
    running_theme_id: str | None,
) -> None:
    """
    Nach ``init_infrastructure``: Boundary auswerten und Pending-Marker setzen
    (Restart-required-Effekte werden beim laufenden Prozess nicht erzwungen).
    """
    if safe_mode_runtime_active():
        return
    preset = get_active_workspace_preset()
    report = build_workspace_preset_boundary_report(
        preset,
        running_gui_id=running_gui_id,
        running_theme_id=running_theme_id,
        safe_mode_runtime_override=False,
    )
    write_full_effect_pending_restart(report.overall_requires_restart)


def resolve_shell_startup_navigation_targets() -> tuple[str, str | None]:
    """
    Liefert ``(area_id, workspace_id)`` für den ersten ``WorkspaceHost.show_area``-Aufruf.

    Safe Mode: konservativ Kommandozentrale. Sonst Nav-Eintrag aus aktivem Preset
    (effektive Startdomain inkl. Registry-Fallback).
    """
    if safe_mode_runtime_active():
        return (NavArea.COMMAND_CENTER, None)

    preset = get_active_workspace_preset()
    compat = build_workspace_preset_compatibility_report(preset)
    token = compat.effective_start_domain
    ent = get_entry(token)
    if ent is None:
        ent = get_entry(FALLBACK_START_DOMAIN_ID)
    if ent is None:
        return (NavArea.COMMAND_CENTER, None)
    return (ent.area, ent.workspace)
