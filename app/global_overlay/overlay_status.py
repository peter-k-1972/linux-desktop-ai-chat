"""
Statusdaten für das Overlay aus Registry / Release-Info (keine Theme-Logik).
"""

from __future__ import annotations

from app import application_release_info as rel
from app.global_overlay.overlay_models import OverlayStatusSnapshot
from app.gui_registry import (
    GUI_ID_DEFAULT_WIDGET,
    get_default_fallback_gui_id,
    get_gui_descriptor,
)


def collect_overlay_status(active_gui_id: str) -> OverlayStatusSnapshot:
    """
    Sammelt angezeigte Werte. Unbekannte optionale Quellen → ``"unavailable"``.
    """
    desc = get_gui_descriptor(active_gui_id)
    preferred = _safe_read_preferred_gui()
    theme_hint = _safe_theme_style_hint(active_gui_id)

    return OverlayStatusSnapshot(
        product_title="Linux Desktop Chat",
        active_gui_id=desc.gui_id,
        gui_display_name=desc.display_name,
        gui_type=desc.gui_type,
        default_fallback_gui_id=get_default_fallback_gui_id(),
        preferred_gui_id=preferred,
        theme_style_hint=theme_hint,
        app_release_version=rel.APP_RELEASE_VERSION,
        bridge_interface_version=rel.BRIDGE_INTERFACE_VERSION,
        ui_contracts_release_version=rel.UI_CONTRACTS_RELEASE_VERSION,
        backend_bundle_version=rel.BACKEND_BUNDLE_VERSION,
    )


def _safe_read_preferred_gui() -> str:
    try:
        from app.gui_bootstrap import read_preferred_gui_id_from_qsettings

        return read_preferred_gui_id_from_qsettings()
    except Exception:
        return "unavailable"


def _safe_theme_style_hint(active_gui_id: str) -> str:
    try:
        if active_gui_id == GUI_ID_DEFAULT_WIDGET:
            from app.gui.themes import get_theme_manager

            return get_theme_manager().get_current_id()
        from app.services.infrastructure import get_infrastructure

        infra = get_infrastructure()
        tid = getattr(infra.settings, "theme_id", "") or ""
        if tid.strip():
            return f"{tid.strip()} (AppSettings; QML shell)"
        return "QML shell — widget ThemeManager not used (see ui_runtime theme)"
    except Exception:
        return "unavailable"
