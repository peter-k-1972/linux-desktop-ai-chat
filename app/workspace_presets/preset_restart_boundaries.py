"""
Workspace Preset — Restart-/Relaunch-Grenzen (Slice 4).

Reine Auswertung auf Basis der laufenden Shell und Safe-Mode-Status; kein erzwungener Hotswap.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from enum import StrEnum

from app.workspace_presets.preset_models import WorkspacePreset
from app.core.startup_contract import (
    GUI_ID_DEFAULT_WIDGET,
    GUI_ID_LIBRARY_QML,
    gui_supports,
    read_safe_mode_next_launch_pending,
    read_safe_mode_watchdog_banner,
)
from app.workspace_presets.preset_registry import PRESET_ID_RESCUE_MINIMAL


class PresetEffectCategory(StrEnum):
    IMMEDIATE = "immediate"
    RESTART_REQUIRED = "restart_required"
    IGNORED_IN_SAFE_MODE = "ignored_in_safe_mode"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class PresetFieldBoundary:
    """Eine Preset-Dimension mit QA-tauglicher Einordnung."""

    field_name: str
    category: PresetEffectCategory
    detail: str


@dataclass(frozen=True, slots=True)
class WorkspacePresetBoundaryReport:
    """Vollständige Grenzauswertung für Overlay, Aktivierung und Tests."""

    entries: tuple[PresetFieldBoundary, ...]
    overall_requires_restart: bool
    safe_mode_runtime_override_active: bool


def safe_mode_runtime_active() -> bool:
    """True wenn Safe-Mode-Banner oder geplanter Safe-Mode-Start aktiv ist."""
    return bool(read_safe_mode_watchdog_banner() or read_safe_mode_next_launch_pending())


def build_workspace_preset_boundary_report(
    preset: WorkspacePreset,
    *,
    running_gui_id: str,
    running_theme_id: str | None,
    safe_mode_runtime_override: bool | None = None,
) -> WorkspacePresetBoundaryReport:
    """
    Klassifiziert jede Preset-Dimension.

    ``safe_mode_runtime_override``: wenn ``None``, wird :func:`safe_mode_runtime_active` verwendet.
    """
    sm = safe_mode_runtime_active() if safe_mode_runtime_override is None else safe_mode_runtime_override
    run_gui = (running_gui_id or "").strip()
    run_theme = (running_theme_id or "").strip() if running_theme_id is not None else None
    entries: list[PresetFieldBoundary] = []

    # --- gui_id ---
    if sm:
        entries.append(
            PresetFieldBoundary(
                "gui_id",
                PresetEffectCategory.IGNORED_IN_SAFE_MODE,
                "Runtime GUI follows Safe Mode / recovery paths, not the preset target, until recovery is cleared.",
            )
        )
    elif run_gui == preset.gui_id:
        entries.append(
            PresetFieldBoundary(
                "gui_id",
                PresetEffectCategory.IMMEDIATE,
                "Running shell matches preset gui_id.",
            )
        )
    else:
        entries.append(
            PresetFieldBoundary(
                "gui_id",
                PresetEffectCategory.RESTART_REQUIRED,
                "Use the GUI section (relaunch via run_gui_shell.py) to reach the preset's gui_id.",
            )
        )

    # --- theme_id ---
    if sm:
        entries.append(
            PresetFieldBoundary(
                "theme_id",
                PresetEffectCategory.IGNORED_IN_SAFE_MODE,
                "Theme selection follows Safe Mode / recovery; preset theme is not applied at runtime until cleared.",
            )
        )
    elif run_gui != preset.gui_id:
        entries.append(
            PresetFieldBoundary(
                "theme_id",
                PresetEffectCategory.RESTART_REQUIRED,
                "Theme target applies after the preset GUI is active (relaunch first).",
            )
        )
    elif not gui_supports(run_gui, "supports_theme_switching"):
        entries.append(
            PresetFieldBoundary(
                "theme_id",
                PresetEffectCategory.RESTART_REQUIRED,
                "This GUI does not support runtime theme switching; theme follows stored preference on next suitable start.",
            )
        )
    elif run_theme is not None and run_theme == preset.theme_id:
        entries.append(
            PresetFieldBoundary(
                "theme_id",
                PresetEffectCategory.IMMEDIATE,
                "Current theme matches preset (no relaunch needed for theme).",
            )
        )
    else:
        entries.append(
            PresetFieldBoundary(
                "theme_id",
                PresetEffectCategory.IMMEDIATE,
                "Theme can be applied without relaunch via the Theme section (product theme port); Slice 4 does not auto-apply.",
            )
        )

    # --- start_domain ---
    if run_gui != preset.gui_id:
        entries.append(
            PresetFieldBoundary(
                "start_domain",
                PresetEffectCategory.RESTART_REQUIRED,
                "Preferred domain is stored; open it after the preset GUI is active (relaunch if GUI differs).",
            )
        )
    elif run_gui == GUI_ID_LIBRARY_QML:
        entries.append(
            PresetFieldBoundary(
                "start_domain",
                PresetEffectCategory.IMMEDIATE,
                "Stored for product state (QSettings). The Qt Quick library GUI does not map this "
                "navigation-registry token to an initial screen at cold start — use the Widget shell for "
                "automatic first navigation from the preset.",
            )
        )
    elif run_gui == GUI_ID_DEFAULT_WIDGET:
        entries.append(
            PresetFieldBoundary(
                "start_domain",
                PresetEffectCategory.IMMEDIATE,
                "Widget shell applies the stored start_domain on startup as the first workspace view "
                "(navigation registry).",
            )
        )
    else:
        entries.append(
            PresetFieldBoundary(
                "start_domain",
                PresetEffectCategory.IMMEDIATE,
                "Stored as preferred navigation target; consult this GUI's shell documentation for "
                "whether the token is applied at startup.",
            )
        )

    # --- layout_mode ---
    entries.append(
        PresetFieldBoundary(
            "layout_mode",
            PresetEffectCategory.UNSUPPORTED,
            "No product layout engine consumes layout_mode yet.",
        )
    )

    # --- context_profile / overlay_mode / rescue_bias (declarative persistence) ---
    entries.append(
        PresetFieldBoundary(
            "context_profile",
            PresetEffectCategory.IMMEDIATE,
            "Persisted declarative value; shell consumers may follow in later slices.",
        )
    )
    om_detail = "Persisted; overlay and product readers use stored overlay_mode."
    if preset.preset_id == PRESET_ID_RESCUE_MINIMAL:
        om_detail += " (rescue_minimal: aligns with recovery-oriented UX when Safe Mode is cleared.)"
    entries.append(
        PresetFieldBoundary(
            "overlay_mode",
            PresetEffectCategory.IMMEDIATE,
            om_detail,
        )
    )
    rb_detail = "Persisted policy hint for rescue/navigation tone; does not override Safe Mode."
    if preset.preset_id == PRESET_ID_RESCUE_MINIMAL:
        rb_detail += " (rescue_minimal: prefer visible recovery affordances once safe.)"
    entries.append(
        PresetFieldBoundary(
            "rescue_bias",
            PresetEffectCategory.IMMEDIATE,
            rb_detail,
        )
    )

    needs_restart = bool(preset.requires_restart) or any(
        e.category == PresetEffectCategory.RESTART_REQUIRED for e in entries
    )

    return WorkspacePresetBoundaryReport(
        entries=tuple(entries),
        overall_requires_restart=needs_restart,
        safe_mode_runtime_override_active=sm,
    )


def list_entries_by_category(
    report: WorkspacePresetBoundaryReport, cat: PresetEffectCategory
) -> tuple[PresetFieldBoundary, ...]:
    return tuple(e for e in report.entries if e.category == cat)


def format_workspace_preset_boundary_report_rich_html(report: WorkspacePresetBoundaryReport) -> str:
    """Kompakte Overlay-Darstellung (HTML)."""

    def _rows(cat: PresetEffectCategory, title: str, color: str) -> str:
        items = list_entries_by_category(report, cat)
        if not items:
            return ""
        lines = "".join(
            f"<li><code>{html.escape(e.field_name)}</code> — {html.escape(e.detail)}</li>" for e in items
        )
        return f"<p style='margin:4px 0;color:{color};'><b>{html.escape(title)}</b></p><ul style='margin:0 0 8px 16px;'>{lines}</ul>"

    sm_note = ""
    if report.safe_mode_runtime_override_active:
        sm_note = (
            "<p style='margin:4px 0;padding:6px;background:#fff8e1;border:1px solid #e65100;border-radius:4px;'>"
            "<b>Safe Mode override</b> — preset targets for GUI/theme are not driving runtime until recovery is cleared. "
            "Stored preset remains; effects are labelled below.</p>"
        )

    overall = (
        "<p style='margin:6px 0;font-weight:600;color:#1565c0;'>"
        f"Overall: relaunch/restart needed for full alignment: <b>{'yes' if report.overall_requires_restart else 'no'}</b>"
        "</p>"
    )

    parts = [
        sm_note,
        overall,
        _rows(PresetEffectCategory.IMMEDIATE, "Immediate / stored now", "#2e7d32"),
        _rows(PresetEffectCategory.RESTART_REQUIRED, "Requires relaunch or follow-up action", "#c62828"),
        _rows(PresetEffectCategory.IGNORED_IN_SAFE_MODE, "Ignored at runtime (Safe Mode)", "#e65100"),
        _rows(PresetEffectCategory.UNSUPPORTED, "Unsupported in this version", "#616161"),
    ]
    return "<div style='font-size:11px;line-height:1.35;'>" + "".join(p for p in parts if p) + "</div>"
