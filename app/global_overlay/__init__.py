"""
Produktweites Global Overlay (nicht Theme, nicht Domäne).

Slice 1: Host, Alt+Z / Alt+Shift+Z, Status-Dialoge, Watchdog-Vorbereitung.
"""

from app.global_overlay.gui_launch_watchdog import (
    get_gui_launch_watchdog_state,
    note_failed_gui_launch,
    note_successful_gui_launch,
    on_app_session_start,
)
from app.global_overlay.overlay_diagnostics import (
    OverlayDiagnosticsSnapshot,
    collect_overlay_diagnostics,
    format_diagnostics_rich_html,
    format_intro_rich_html,
)
from app.global_overlay.overlay_controller import OverlayController
from app.global_overlay.overlay_host import (
    GlobalOverlayHost,
    detach_global_overlay_host,
    get_overlay_host,
    install_global_overlay_host,
    shortcut_sequences,
)
from app.global_overlay.overlay_models import OverlayStatusSnapshot, OverlaySurfaceKind
from app.global_overlay.overlay_rescue_port import (
    RescueResult,
    rescue_disable_safe_mode_watchdog,
    rescue_enable_safe_mode_next_launch,
    rescue_reset_preferred_gui_only,
    rescue_reset_preferred_theme_only,
    rescue_restart_application,
    rescue_revert_to_default_gui_relaunch,
)
from app.global_overlay.overlay_gui_port import (
    GuiApplyResult,
    GuiOverlaySnapshot,
    apply_gui_switch_via_product,
    build_gui_overlay_snapshot,
    relaunch_via_run_gui_shell,
    revert_to_default_gui_via_product,
    validate_gui_switch_target,
)
from app.global_overlay.overlay_theme_port import (
    ThemeApplyEffect,
    ThemeApplyResult,
    ThemeOverlaySnapshot,
    apply_theme_via_product,
    build_theme_overlay_snapshot,
)

__all__ = [
    "OverlayDiagnosticsSnapshot",
    "collect_overlay_diagnostics",
    "format_diagnostics_rich_html",
    "format_intro_rich_html",
    "GlobalOverlayHost",
    "OverlayController",
    "OverlayStatusSnapshot",
    "OverlaySurfaceKind",
    "GuiApplyResult",
    "GuiOverlaySnapshot",
    "RescueResult",
    "ThemeApplyEffect",
    "ThemeApplyResult",
    "ThemeOverlaySnapshot",
    "apply_gui_switch_via_product",
    "apply_theme_via_product",
    "build_gui_overlay_snapshot",
    "build_theme_overlay_snapshot",
    "relaunch_via_run_gui_shell",
    "rescue_disable_safe_mode_watchdog",
    "rescue_enable_safe_mode_next_launch",
    "rescue_reset_preferred_gui_only",
    "rescue_reset_preferred_theme_only",
    "rescue_restart_application",
    "rescue_revert_to_default_gui_relaunch",
    "revert_to_default_gui_via_product",
    "validate_gui_switch_target",
    "get_gui_launch_watchdog_state",
    "detach_global_overlay_host",
    "get_overlay_host",
    "install_global_overlay_host",
    "note_failed_gui_launch",
    "note_successful_gui_launch",
    "on_app_session_start",
    "shortcut_sequences",
]
