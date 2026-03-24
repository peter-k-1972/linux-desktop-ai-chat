"""
Workspace Preset — Aktivierung (Slice 3–4): Auswertung, Persistenz, Restart-Grenzen.

Kein erzwungener GUI-Hotswap; Relaunch bleibt der sichere Produktpfad (GUI-Sektion / Launcher).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.gui_bootstrap import read_safe_mode_next_launch_pending, read_safe_mode_watchdog_banner

from app.workspace_presets.preset_models import PresetReleaseStatus, WorkspacePreset
from app.gui_registry import get_default_fallback_gui_id

from app.workspace_presets.preset_registry import get_default_workspace_preset_id, get_workspace_preset
from app.workspace_presets.preset_restart_boundaries import (
    WorkspacePresetBoundaryReport,
    build_workspace_preset_boundary_report,
    safe_mode_runtime_active,
)
from app.workspace_presets.preset_compatibility import (
    WorkspacePresetCompatibilityReport,
    build_workspace_preset_compatibility_report,
)
from app.workspace_presets.preset_state import (
    resolve_valid_active_workspace_preset_id,
    write_active_workspace_preset_bundle_to_storage,
    write_full_effect_pending_restart,
)
from app.workspace_presets.preset_validation import validate_workspace_preset


class WorkspacePresetActivationStatus(StrEnum):
    """QA-/Overlay-transparenter Aktivierungsstatus."""

    REJECTED = "rejected"
    ACCEPTED_IMMEDIATE = "accepted_immediate"
    ACCEPTED_PENDING_RESTART = "accepted_pending_restart"


@dataclass(frozen=True, slots=True)
class WorkspacePresetActivationResult:
    ok: bool
    status: WorkspacePresetActivationStatus
    message: str
    restart_required_for_full_effect: bool
    """Spiegel von ``boundary_report.overall_requires_restart`` bei Erfolg."""
    active_preset_id: str | None = None
    boundary_report: WorkspacePresetBoundaryReport | None = None
    """Nur bei erfolgreicher Auswertung/Aktivierung (Safe Mode aus); sonst ``None``."""
    partial_activation: bool = False
    """True wenn GUI ok, aber Theme oder Startdomain nur teilweise / mit Fallback."""
    compatibility_report: WorkspacePresetCompatibilityReport | None = None


def _safe_mode_blocks_activation() -> tuple[bool, str]:
    if read_safe_mode_watchdog_banner():
        return True, "Safe Mode (recovery) is active — workspace preset changes are blocked until recovery is cleared."
    if read_safe_mode_next_launch_pending():
        return (
            True,
            "Safe mode is scheduled for the next launch — workspace preset activation is blocked.",
        )
    return False, ""


def resync_full_effect_pending_restart_from_runtime(
    *,
    running_gui_id: str,
    running_theme_id: str | None,
) -> None:
    """
    Stellt den QSettings-Marker an die aktuelle Laufzeit aus (ohne Safe Mode: keine Anpassung).

    Aufruf z. B. beim Öffnen des Overlays.
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


def evaluate_workspace_preset_activation(
    preset_id: str,
    *,
    running_gui_id: str,
    running_theme_id: str | None = None,
) -> WorkspacePresetActivationResult:
    """
    Rein deklarative Auswertung ohne Persistenz (Tests, Vorab-Checks).
    """
    key = (preset_id or "").strip()
    if not key:
        return WorkspacePresetActivationResult(
            ok=False,
            status=WorkspacePresetActivationStatus.REJECTED,
            message="No preset selected.",
            restart_required_for_full_effect=False,
            active_preset_id=None,
            boundary_report=None,
        )

    blocked, why = _safe_mode_blocks_activation()
    if blocked:
        return WorkspacePresetActivationResult(
            ok=False,
            status=WorkspacePresetActivationStatus.REJECTED,
            message=why,
            restart_required_for_full_effect=False,
            active_preset_id=None,
            boundary_report=None,
        )

    try:
        preset = get_workspace_preset(key)
    except KeyError:
        return WorkspacePresetActivationResult(
            ok=False,
            status=WorkspacePresetActivationStatus.REJECTED,
            message=f"Unknown preset: {key!r}.",
            restart_required_for_full_effect=False,
            active_preset_id=None,
            boundary_report=None,
        )

    if preset.release_status == PresetReleaseStatus.DEPRECATED:
        return WorkspacePresetActivationResult(
            ok=False,
            status=WorkspacePresetActivationStatus.REJECTED,
            message="This preset is deprecated and cannot be activated.",
            restart_required_for_full_effect=False,
            active_preset_id=None,
            boundary_report=None,
        )

    if preset.release_status != PresetReleaseStatus.APPROVED:
        return WorkspacePresetActivationResult(
            ok=False,
            status=WorkspacePresetActivationStatus.REJECTED,
            message="Only approved presets can be activated.",
            restart_required_for_full_effect=False,
            active_preset_id=None,
            boundary_report=None,
        )

    errs = validate_workspace_preset(preset)
    if errs:
        return WorkspacePresetActivationResult(
            ok=False,
            status=WorkspacePresetActivationStatus.REJECTED,
            message="Invalid preset: " + "; ".join(errs),
            restart_required_for_full_effect=False,
            active_preset_id=None,
            boundary_report=None,
        )

    compat = build_workspace_preset_compatibility_report(preset)
    if not compat.activation_allowed:
        return WorkspacePresetActivationResult(
            ok=False,
            status=WorkspacePresetActivationStatus.REJECTED,
            message="Preset activation rejected (compatibility): " + "; ".join(compat.issues),
            restart_required_for_full_effect=False,
            active_preset_id=None,
            boundary_report=None,
            compatibility_report=compat,
        )

    report = build_workspace_preset_boundary_report(
        preset,
        running_gui_id=running_gui_id,
        running_theme_id=running_theme_id,
        safe_mode_runtime_override=False,
    )
    need_restart = report.overall_requires_restart
    st = (
        WorkspacePresetActivationStatus.ACCEPTED_PENDING_RESTART
        if need_restart
        else WorkspacePresetActivationStatus.ACCEPTED_IMMEDIATE
    )
    partial = not compat.fully_compatible
    partial_note = ""
    if partial:
        partial_note = " Compatibility note(s): " + " ".join(compat.issues)
    if need_restart:
        msg = (
            "Preset accepted (preview). Persisting will store targets; full effect needs relaunch or follow-up "
            "(see boundary: GUI/theme/start_domain as applicable). Use the GUI/Theme sections — no auto-relaunch here."
            + partial_note
        )
    else:
        msg = (
            "Preset accepted (preview). Declarative fields align with this shell for restart boundaries; "
            "layout_mode remains unsupported."
            + partial_note
        )
    return WorkspacePresetActivationResult(
        ok=True,
        status=st,
        message=msg,
        restart_required_for_full_effect=need_restart,
        active_preset_id=preset.preset_id,
        boundary_report=report,
        partial_activation=partial,
        compatibility_report=compat,
    )


def apply_workspace_preset_activation(
    preset_id: str,
    *,
    running_gui_id: str,
    running_theme_id: str | None = None,
) -> WorkspacePresetActivationResult:
    """
    Bewertet und persistiert bei Erfolg; setzt ``full_effect_pending_restart``-Marker aus BoundaryReport.
    """
    ev = evaluate_workspace_preset_activation(
        preset_id, running_gui_id=running_gui_id, running_theme_id=running_theme_id
    )
    if not ev.ok or ev.active_preset_id is None:
        return ev

    compat = ev.compatibility_report
    assert compat is not None
    write_active_workspace_preset_bundle_to_storage(
        ev.active_preset_id,
        start_domain_override=compat.effective_start_domain if not compat.domain_ok else None,
        sync_preferred_gui=True,
        sync_preferred_theme=True,
        persist_theme_from_preset=compat.theme_ok,
    )
    assert ev.boundary_report is not None
    write_full_effect_pending_restart(ev.boundary_report.overall_requires_restart)
    tail = (
        "Full effect requires relaunch or manual GUI/theme follow-up — see Restart boundaries below."
        if ev.boundary_report.overall_requires_restart
        else "Restart boundaries show no relaunch requirement for declared targets on this shell."
    )
    if ev.partial_activation:
        tail += " Partial activation: see compatibility notes in the preview message."
    return WorkspacePresetActivationResult(
        ok=True,
        status=ev.status,
        message="Preset activated and persisted. " + tail,
        restart_required_for_full_effect=ev.boundary_report.overall_requires_restart,
        active_preset_id=ev.active_preset_id,
        boundary_report=ev.boundary_report,
        partial_activation=ev.partial_activation,
        compatibility_report=compat,
    )


def get_active_workspace_preset() -> WorkspacePreset:
    """Liefert das aktuell gültige persistierte Preset (aufgelöst inkl. Fallback)."""
    pid = resolve_valid_active_workspace_preset_id()
    return get_workspace_preset(pid)


def get_active_workspace_preset_id() -> str:
    return resolve_valid_active_workspace_preset_id()


def set_active_workspace_preset(
    preset_id: str,
    *,
    running_gui_id: str,
    running_theme_id: str | None = None,
) -> WorkspacePresetActivationResult:
    """Alias für :func:`apply_workspace_preset_activation` (öffentliche Produkt-API)."""
    return apply_workspace_preset_activation(
        preset_id, running_gui_id=running_gui_id, running_theme_id=running_theme_id
    )


def clear_active_workspace_preset(
    *,
    running_gui_id: str = "",
    running_theme_id: str | None = None,
) -> WorkspacePresetActivationResult:
    """
    Setzt den gespeicherten Zustand auf das Registry-Default-Preset (kein „leerer“ Zustand).

    Respektiert Safe Mode wie Aktivierung.
    """
    default_id = get_default_workspace_preset_id()
    blocked, why = _safe_mode_blocks_activation()
    if blocked:
        return WorkspacePresetActivationResult(
            ok=False,
            status=WorkspacePresetActivationStatus.REJECTED,
            message=why,
            restart_required_for_full_effect=False,
            active_preset_id=None,
            boundary_report=None,
        )
    write_active_workspace_preset_bundle_to_storage(default_id)
    preset = get_workspace_preset(default_id)
    gid = (running_gui_id or "").strip() or get_default_fallback_gui_id()
    report = build_workspace_preset_boundary_report(
        preset,
        running_gui_id=gid,
        running_theme_id=running_theme_id,
        safe_mode_runtime_override=False,
    )
    write_full_effect_pending_restart(report.overall_requires_restart)
    st = (
        WorkspacePresetActivationStatus.ACCEPTED_PENDING_RESTART
        if report.overall_requires_restart
        else WorkspacePresetActivationStatus.ACCEPTED_IMMEDIATE
    )
    return WorkspacePresetActivationResult(
        ok=True,
        status=st,
        message=f"Active workspace preset reset to default ({default_id!r}).",
        restart_required_for_full_effect=report.overall_requires_restart,
        active_preset_id=default_id,
        boundary_report=report,
        partial_activation=False,
        compatibility_report=build_workspace_preset_compatibility_report(preset),
    )
