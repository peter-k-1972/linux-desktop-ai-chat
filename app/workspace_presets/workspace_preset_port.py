"""
Workspace Presets — Overlay-Anbindung (Slice 2–4).

Slice 4: Restart-/Relaunch-Grenzen, persistierter Pending-Marker, ehrliche Overlay-Kommunikation.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from typing import Final

from app.workspace_presets.preset_activation import (
    WorkspacePresetActivationResult,
    apply_workspace_preset_activation,
    resync_full_effect_pending_restart_from_runtime,
)
from app.workspace_presets.preset_models import WorkspacePreset
from app.workspace_presets.preset_registry import (
    get_default_workspace_preset_id,
    get_workspace_preset,
    list_approved_workspace_presets,
)
from app.workspace_presets.preset_restart_boundaries import (
    WorkspacePresetBoundaryReport,
    build_workspace_preset_boundary_report,
    format_workspace_preset_boundary_report_rich_html,
    safe_mode_runtime_active,
)
from app.workspace_presets.preset_state import (
    read_full_effect_pending_restart,
    resolve_valid_active_workspace_preset_id,
)

SLICE4_OVERLAY_NOTICE_HTML: Final[str] = (
    "<b>Workspace presets (Slice 4)</b><br/>"
    "<b>Activate preset</b> persists targets and records whether a <b>relaunch or manual GUI/theme step</b> is still "
    "needed — see <b>Restart boundaries</b>. No automatic GUI hotswap; use the <b>GUI</b> section / "
    "<code>run_gui_shell.py</code> when required. "
    "<b>Safe Mode</b> blocks changing the active preset; while active, runtime GUI/theme follow preset targets only after recovery.<br/>"
    "<span style='color:#555;'>Theme can often be applied from the Theme section without relaunch when the GUI supports it.</span>"
)

SLICE5_OVERLAY_NOTICE_HTML: Final[str] = (
    "<b>Workspace presets (Slice 5 — product integration)</b><br/>"
    "A preset is a <b>work mode</b> for the whole product: it configures GUI, theme, start workspace, overlay hints, "
    "and rescue bias — it does not replace those subsystems. "
    "At application start, immediate effects apply; restart-required parts are deferred to relaunch (see boundaries). "
    "<b>Safe Mode</b> and explicit <code>--gui</code> / <code>--theme</code> / env overrides take precedence "
    "<b>per dimension</b> (e.g. a theme override does not block syncing the preset bundle or GUI target from storage). "
    "<b>Widget shell</b> applies <code>start_domain</code> on startup; the <b>Qt Quick library GUI</b> persists the "
    "token for product state but does not map it to an initial QML screen at cold start — see <b>Restart boundaries</b>."
)

SLICE3_OVERLAY_NOTICE_HTML: Final[str] = SLICE5_OVERLAY_NOTICE_HTML
SLICE2_PRELIMINARY_NOTICE_HTML: Final[str] = SLICE5_OVERLAY_NOTICE_HTML


@dataclass(frozen=True, slots=True)
class WorkspacePresetOverlaySnapshot:
    """
    Read-only Snapshot für Overlay und Tests.

    ``session_override_active`` ist ab Slice 3 immer False (Historie Slice-2-Session-Override).
    """

    effective_preset_id: str
    registry_default_preset_id: str
    session_override_active: bool
    selectable_preset_ids: tuple[str, ...]
    active_full_effect_requires_restart: bool
    safe_mode_runtime_override_active: bool


def build_active_workspace_preset_boundary_report_for_overlay(
    *,
    running_gui_id: str,
    running_theme_id: str | None,
) -> WorkspacePresetBoundaryReport:
    """Resynchronisiert Pending-Marker und liefert den Boundary-Report für die Anzeige (inkl. Safe-Mode-Hinweise)."""
    from app.workspace_presets.preset_activation import get_active_workspace_preset

    resync_full_effect_pending_restart_from_runtime(
        running_gui_id=running_gui_id, running_theme_id=running_theme_id
    )
    preset = get_active_workspace_preset()
    return build_workspace_preset_boundary_report(
        preset,
        running_gui_id=running_gui_id,
        running_theme_id=running_theme_id,
        safe_mode_runtime_override=None,
    )


def get_registry_default_preset_id() -> str:
    return get_default_workspace_preset_id()


def get_effective_active_workspace_preset_id() -> str:
    return resolve_valid_active_workspace_preset_id()


def get_effective_preset_id_for_session() -> str:
    return get_effective_active_workspace_preset_id()


def list_selectable_presets_for_overlay() -> tuple[WorkspacePreset, ...]:
    return list_approved_workspace_presets()


def build_workspace_preset_overlay_snapshot(
    *,
    running_gui_id: str,
    running_theme_id: str | None = None,
) -> WorkspacePresetOverlaySnapshot:
    """
    Liest Zustand nach :func:`resync_full_effect_pending_restart_from_runtime`
    (typischerweise direkt nach :func:`build_active_workspace_preset_boundary_report_for_overlay`).
    """
    eff = resolve_valid_active_workspace_preset_id()
    default_id = get_default_workspace_preset_id()
    sel = tuple(p.preset_id for p in list_selectable_presets_for_overlay())
    pending = read_full_effect_pending_restart()
    return WorkspacePresetOverlaySnapshot(
        effective_preset_id=eff,
        registry_default_preset_id=default_id,
        session_override_active=False,
        selectable_preset_ids=sel,
        active_full_effect_requires_restart=pending,
        safe_mode_runtime_override_active=safe_mode_runtime_active(),
    )


def request_preset_activation(
    preset_id: str,
    *,
    running_gui_id: str,
    running_theme_id: str | None = None,
) -> WorkspacePresetActivationResult:
    return apply_workspace_preset_activation(
        preset_id, running_gui_id=running_gui_id, running_theme_id=running_theme_id
    )


def format_workspace_preset_tags_rich_html(preset: WorkspacePreset) -> str:
    """Kompakte Tag-Zeile für Overlay (Arbeitsmodus-Label)."""
    if not preset.tags:
        return "<span style='color:#888;'>—</span>"
    chips = " · ".join(
        f"<span style='background:#eceff1;border-radius:3px;padding:1px 6px;font-size:11px;'>{html.escape(t)}</span>"
        for t in preset.tags
    )
    return chips


def format_workspace_preset_detail_rich_html(preset: WorkspacePreset) -> str:
    tags = ", ".join(html.escape(t) for t in preset.tags) if preset.tags else "—"
    return (
        f"<div style='font-size:12px;line-height:1.4;color:#222;'>"
        f"<b>{html.escape(preset.display_name)}</b> "
        f"<code>({html.escape(preset.preset_id)})</code><br/>"
        f"<span style='color:#444;'>{html.escape(preset.description)}</span><br/><br/>"
        f"<table style='border-collapse:collapse;font-size:11px;'>"
        f"<tr><td style='padding:2px 8px 2px 0;color:#666;'>gui_id</td>"
        f"<td><code>{html.escape(preset.gui_id)}</code></td></tr>"
        f"<tr><td style='padding:2px 8px 2px 0;color:#666;'>theme_id</td>"
        f"<td><code>{html.escape(preset.theme_id)}</code></td></tr>"
        f"<tr><td style='padding:2px 8px 2px 0;color:#666;'>start_domain</td>"
        f"<td><code>{html.escape(preset.start_domain)}</code></td></tr>"
        f"<tr><td style='padding:2px 8px 2px 0;color:#666;'>layout_mode</td>"
        f"<td><code>{html.escape(preset.layout_mode)}</code></td></tr>"
        f"<tr><td style='padding:2px 8px 2px 0;color:#666;'>context_profile</td>"
        f"<td><code>{html.escape(preset.context_profile)}</code></td></tr>"
        f"<tr><td style='padding:2px 8px 2px 0;color:#666;'>requires_restart</td>"
        f"<td><code>{str(preset.requires_restart).lower()}</code> (declarative)</td></tr>"
        f"<tr><td style='padding:2px 8px 2px 0;color:#666;'>release_status</td>"
        f"<td><code>{html.escape(preset.release_status.value)}</code></td></tr>"
        f"<tr><td style='padding:2px 8px 2px 0;color:#666;'>tags</td>"
        f"<td>{tags}</td></tr>"
        f"</table>"
        f"<p style='margin:8px 0 0 0;color:#555;font-size:11px;'>"
        f"A workspace preset is a <b>product work mode</b> (composition), not a GUI row or a theme."
        f"</p></div>"
    )
