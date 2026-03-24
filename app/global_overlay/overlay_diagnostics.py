"""
Read-only Diagnostik und Kompatibilitäts-Kurzinfos für das produktweite Overlay (Slice 5).

Keine Secrets, keine Rohlogs, keine Debug-Konsole — nur aggregierte, sicher lesbare Labels.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from app import application_release_info as rel
from app.global_overlay.overlay_gui_port import build_gui_overlay_snapshot, validate_gui_switch_target
from app.global_overlay.overlay_product_shortcuts import (
    OVERLAY_TOGGLE_EMERGENCY_SHORTCUT,
    OVERLAY_TOGGLE_NORMAL_SHORTCUT,
)
from app.global_overlay.overlay_theme_port import build_theme_overlay_snapshot
from app.global_overlay.overlay_status import collect_overlay_status
from app.gui_capabilities import get_capabilities_for_gui_id
from app.gui_registry import GUI_ID_LIBRARY_QML, resolve_repo_root


def _truncate(text: str, max_len: int = 96) -> str:
    t = (text or "").strip().replace("\n", " ")
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


@dataclass(frozen=True, slots=True)
class OverlayDiagnosticsSnapshot:
    """Alle angezeigten Diagnosefelder (reine Anzeige, keine Aktionen)."""

    app_release_version: str
    backend_bundle_version: str
    contracts_version: str
    bridge_version: str
    active_gui_id: str
    active_theme_or_style: str
    fallback_gui_id: str
    safe_mode_next_launch: str
    safe_mode_overlay_status: str  # inactive | pending next launch | watchdog session | kombiniert
    watchdog_failures_in_window: str
    manifest_short_status: str
    release_status: str
    compatibility_status: str
    gui_compatibility_check: str
    theme_switching_support: str
    gui_switching_support: str
    global_overlay_product_status: str
    """Global Overlay als Produktlayer (nicht GUI-Capability)."""
    capability_rows: tuple[tuple[str, str], ...]
    """(Kurzlabel, yes|no|unavailable)."""


def _safe_bool_pending_safe_mode() -> str:
    try:
        from app.gui_bootstrap import read_safe_mode_next_launch_pending

        return "yes" if read_safe_mode_next_launch_pending() else "no"
    except Exception:
        return "unavailable"


def _safe_mode_overlay_status_label() -> str:
    try:
        from app.gui_bootstrap import read_safe_mode_next_launch_pending, read_safe_mode_watchdog_banner

        pending = read_safe_mode_next_launch_pending()
        banner = read_safe_mode_watchdog_banner()
        if pending and banner:
            return "pending next launch; watchdog session active"
        if pending:
            return "pending next launch"
        if banner:
            return "active (watchdog session)"
        return "inactive"
    except Exception:
        return "unavailable"


def _product_global_overlay_status_label() -> str:
    try:
        from PySide6.QtWidgets import QApplication

        from app.global_overlay.overlay_host import get_overlay_host

        app = QApplication.instance()
        if app is None:
            return "unavailable"
        return "active (this session)" if get_overlay_host(app) is not None else "not loaded"
    except Exception:
        return "unavailable"


def _watchdog_failures_window_label() -> str:
    try:
        from app.global_overlay.gui_launch_watchdog import read_persisted_watchdog_snapshot_for_diagnostics

        snap = read_persisted_watchdog_snapshot_for_diagnostics()
        return snap.get("failures_in_window", "unavailable")
    except Exception:
        return "unavailable"


def _manifest_and_release_for_gui(active_gui_id: str) -> tuple[str, str, str]:
    """
    Returns:
        (manifest_short_status, release_status_from_manifest, qml_runtime_compat_hint)
    """
    if active_gui_id != GUI_ID_LIBRARY_QML:
        return (
            "not applicable (widget GUI does not use qml/theme_manifest.json)",
            "unavailable",
            "unavailable",
        )
    root = resolve_repo_root()
    try:
        from app.qml_theme_governance import (
            assert_qml_theme_runtime_compatible,
            load_qml_theme_manifest_dict,
            validate_qml_theme_manifest_shape,
        )

        data = load_qml_theme_manifest_dict(root)
        validate_qml_theme_manifest_shape(data)
        assert_qml_theme_runtime_compatible(
            data,
            app_version=rel.APP_RELEASE_VERSION,
            backend_version=rel.BACKEND_BUNDLE_VERSION,
            contract_version=rel.UI_CONTRACTS_RELEASE_VERSION,
            bridge_version=rel.BRIDGE_INTERFACE_VERSION,
        )
        rs = str(data.get("release_status") or "").strip() or "unavailable"
        tv = str(data.get("theme_version") or "").strip() or "unavailable"
        short = f"theme_manifest.json present; theme_version={tv}; release_status={rs}"
        return (short, rs, "ok (runtime labels in manifest allow-lists)")
    except FileNotFoundError as e:
        return (f"unavailable ({_truncate(html.escape(str(e)))})", "unavailable", "unavailable")
    except ValueError as e:
        return (
            f"issue ({_truncate(html.escape(str(e)))})",
            "unavailable",
            f"failed ({_truncate(html.escape(str(e)))})",
        )
    except Exception as e:
        return (
            f"unavailable ({_truncate(html.escape(str(e)))})",
            "unavailable",
            "unavailable",
        )


def _gui_switch_label(gs) -> str:
    if gs.gui_switching_available:
        return "yes"
    if gs.gui_switching_block_reason:
        return f"no ({_truncate(html.escape(gs.gui_switching_block_reason))})"
    return "no"


def _theme_switch_label(ts) -> str:
    if ts.switching_supported:
        return "yes"
    if ts.switching_block_reason:
        return f"no ({_truncate(html.escape(ts.switching_block_reason))})"
    return "no"


def _evaluate_active_gui_registry_check(active_gui_id: str) -> str:
    try:
        ok, err = validate_gui_switch_target(active_gui_id)
        if ok:
            return "ok (registry, entrypoint, manifest rules)"
        return f"failed ({_truncate(html.escape(err))})"
    except Exception as e:
        return f"unavailable ({_truncate(html.escape(str(e)))})"


def _build_capability_rows(active_gui_id: str) -> tuple[tuple[str, str], ...]:
    try:
        caps = get_capabilities_for_gui_id(active_gui_id)
    except Exception:
        return tuple((label, "unavailable") for label, _ in _CAPABILITY_FIELDS)

    rows: list[tuple[str, str]] = []
    for label, attr in _CAPABILITY_FIELDS:
        try:
            v = getattr(caps, attr)
            rows.append((label, "yes" if v else "no"))
        except Exception:
            rows.append((label, "unavailable"))
    return tuple(rows)


_CAPABILITY_FIELDS: tuple[tuple[str, str], ...] = (
    ("chat", "supports_chat"),
    ("projects", "supports_projects"),
    ("workflows", "supports_workflows"),
    ("prompts", "supports_prompts"),
    ("agents", "supports_agents"),
    ("deployment", "supports_deployment"),
    ("settings", "supports_settings"),
    ("theme switching", "supports_theme_switching"),
)


def collect_overlay_diagnostics(active_gui_id: str) -> OverlayDiagnosticsSnapshot:
    """
    Sammelt angezeigte Diagnosewerte.

    Unbekannte oder riskante Quellen liefern ``unavailable`` bzw. kurze, escapte Hinweise.
    """
    base = collect_overlay_status(active_gui_id)
    gs = build_gui_overlay_snapshot(active_gui_id)
    ts = build_theme_overlay_snapshot(active_gui_id)
    manifest_short, manifest_release, qml_compat = _manifest_and_release_for_gui(active_gui_id)
    gui_check = _evaluate_active_gui_registry_check(active_gui_id)

    # Release status: manifest wins for QML; else product label only
    if active_gui_id == GUI_ID_LIBRARY_QML and manifest_release != "unavailable":
        release_status = manifest_release
    else:
        release_status = "unavailable"

    # Compatibility status: combine GUI registry check + QML list check when applicable
    parts: list[str] = []
    if gui_check.startswith("ok"):
        parts.append("GUI definition ok")
    elif gui_check.startswith("unavailable"):
        parts.append("GUI check unavailable")
    else:
        parts.append("GUI definition issue")

    if active_gui_id == GUI_ID_LIBRARY_QML:
        if qml_compat.startswith("ok"):
            parts.append("QML manifest/runtime ok")
        elif qml_compat == "unavailable":
            parts.append("QML manifest check unavailable")
        else:
            parts.append("QML manifest/runtime issue")

    compatibility_status = "; ".join(parts) if parts else "unavailable"

    return OverlayDiagnosticsSnapshot(
        app_release_version=base.app_release_version,
        backend_bundle_version=base.backend_bundle_version,
        contracts_version=base.ui_contracts_release_version,
        bridge_version=base.bridge_interface_version,
        active_gui_id=base.active_gui_id,
        active_theme_or_style=base.theme_style_hint,
        fallback_gui_id=base.default_fallback_gui_id,
        safe_mode_next_launch=_safe_bool_pending_safe_mode(),
        safe_mode_overlay_status=_safe_mode_overlay_status_label(),
        watchdog_failures_in_window=_watchdog_failures_window_label(),
        manifest_short_status=manifest_short,
        release_status=release_status,
        compatibility_status=compatibility_status,
        gui_compatibility_check=gui_check,
        theme_switching_support=_theme_switch_label(ts),
        gui_switching_support=_gui_switch_label(gs),
        global_overlay_product_status=_product_global_overlay_status_label(),
        capability_rows=_build_capability_rows(active_gui_id),
    )


def format_diagnostics_rich_html(d: OverlayDiagnosticsSnapshot) -> str:
    """Kompaktes Rich-HTML für ein schreibgeschütztes QLabel (ruhige Produktoptik)."""
    cap_lines = "".join(
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>{html.escape(name)}</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(val)}</code></td></tr>"
        for name, val in d.capability_rows
    )
    return (
        f"<div style='color:#333;font-size:12px;line-height:1.45;'>"
        f"<p style='margin:0 0 8px 0;'><b>Diagnostics</b> (read-only)</p>"
        f"<table style='border-collapse:collapse;width:100%;'>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>App release</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.app_release_version)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Backend bundle</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.backend_bundle_version)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>UI contracts</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.contracts_version)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Bridge</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.bridge_version)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Active GUI</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.active_gui_id)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Active theme / style</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.active_theme_or_style)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Fallback GUI</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.fallback_gui_id)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Safe mode next launch</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.safe_mode_next_launch)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Safe mode (status)</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.safe_mode_overlay_status)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Watchdog failures (10s window)</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.watchdog_failures_in_window)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Global overlay (product)</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.global_overlay_product_status)}</code></td></tr>"
        f"<tr><td colspan='2' style='padding:10px 0 4px 0;'><b>Release / compatibility</b></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Release status</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.release_status)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;vertical-align:top;'>Compatibility</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.compatibility_status)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;vertical-align:top;'>GUI compatibility check</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.gui_compatibility_check)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>Theme switching (this GUI)</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.theme_switching_support)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;'>GUI switching (product)</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.gui_switching_support)}</code></td></tr>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555;vertical-align:top;'>Manifest / manifest status</td>"
        f"<td style='padding:2px 0;'><code>{html.escape(d.manifest_short_status)}</code></td></tr>"
        f"<tr><td colspan='2' style='padding:10px 0 4px 0;'><b>Active GUI capabilities</b></td></tr>"
        f"{cap_lines}"
        f"</table>"
        f"<p style='margin:10px 0 0 0;color:#666;font-size:11px;'>"
        f"Shortcuts: <code>{html.escape(OVERLAY_TOGGLE_NORMAL_SHORTCUT)}</code> — system overlay · "
        f"<code>{html.escape(OVERLAY_TOGGLE_EMERGENCY_SHORTCUT)}</code> — emergency overlay · "
        f"<code>Esc</code> — close"
        f"</p></div>"
    )


def format_intro_rich_html(product_title: str) -> str:
    """Kurzer Kopf ohne doppelte Versionszeilen (die stehen unter Diagnostics)."""
    return (
        f"<div style='color:#222;font-size:13px;line-height:1.5;'>"
        f"<b>{html.escape(product_title)}</b> — System menu<br/>"
        f"<span style='color:#555;'>Use the sections below for GUI, theme, and rescue actions. "
        f"Diagnostics are read-only.</span>"
        f"</div>"
    )
