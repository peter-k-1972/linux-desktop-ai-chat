"""
Produkt-Adapter: Theme-Status und -Wechsel für das Overlay (kein Theme-Subsystem).

Widget-GUI: ThemeManager + ServiceSettingsAdapter (wie Settings / Appearance).
QML-GUI: nur Read-only; Wechsel blockiert über ``supports_theme_switching``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from app.core.startup_contract import (
    apply_product_theme_visual,
    current_product_theme_id,
    list_registered_product_themes,
    GUI_ID_DEFAULT_WIDGET,
    get_gui_descriptor,
    gui_supports,
)

_THEME_IMMEDIATE_HELP: Final[str] = (
    "Changes apply immediately to the widget GUI (stylesheet + persisted preference)."
)
_THEME_RESTART_HELP: Final[str] = (
    "A restart or relaunch would be required for this GUI to apply a new theme "
    "(not available in this slice for the QML shell)."
)


class ThemeApplyEffect(str, Enum):
    """Wie sich ein erfolgreicher Wechsel auswirkt."""

    IMMEDIATE = "immediate"
    RESTART_REQUIRED = "restart_required"
    NOT_AVAILABLE = "not_available"


@dataclass(frozen=True, slots=True)
class ThemeOverlaySnapshot:
    """Theme-Bezug nur für Overlay (Slice 2)."""

    active_gui_id: str
    current_theme_id: str
    switching_supported: bool
    switching_block_reason: str | None
    apply_effect: ThemeApplyEffect
    apply_effect_user_hint: str
    allowed_themes: tuple[tuple[str, str], ...]
    """(theme_id, display_name) — nur freigegebene Einträge der Registry."""


@dataclass(frozen=True, slots=True)
class ThemeApplyResult:
    ok: bool
    message: str


def _supports_theme_switching_cap(active_gui_id: str) -> bool:
    try:
        return gui_supports(active_gui_id, "supports_theme_switching")
    except Exception:
        return False


def _current_theme_id_for_gui(active_gui_id: str) -> str:
    try:
        if active_gui_id == GUI_ID_DEFAULT_WIDGET:
            tid = current_product_theme_id()
            return tid if tid else "unavailable"
        from app.services.infrastructure import get_infrastructure

        infra = get_infrastructure()
        raw = (getattr(infra.settings, "theme_id", "") or "").strip()
        return raw if raw else "unavailable"
    except Exception:
        return "unavailable"


def build_theme_overlay_snapshot(active_gui_id: str) -> ThemeOverlaySnapshot:
    """
    Liest Theme-Status ausschließlich über Produktpfade.

    Keine Theme-Dateizugriffe; Liste nur aus ThemeManager-Registry (Widget-Pfad).
    """
    desc = get_gui_descriptor(active_gui_id)
    cap_ok = _supports_theme_switching_cap(active_gui_id)
    current = _current_theme_id_for_gui(active_gui_id)

    if not cap_ok:
        reason = (
            f"GUI {desc.gui_id!r} does not declare supports_theme_switching "
            f"(see app.core.startup_contract)."
        )
        return ThemeOverlaySnapshot(
            active_gui_id=active_gui_id,
            current_theme_id=current,
            switching_supported=False,
            switching_block_reason=reason,
            apply_effect=ThemeApplyEffect.NOT_AVAILABLE,
            apply_effect_user_hint=_THEME_RESTART_HELP,
            allowed_themes=(),
        )

    if active_gui_id != GUI_ID_DEFAULT_WIDGET:
        return ThemeOverlaySnapshot(
            active_gui_id=active_gui_id,
            current_theme_id=current,
            switching_supported=False,
            switching_block_reason="Theme switching via overlay is only wired for the widget GUI in this product phase.",
            apply_effect=ThemeApplyEffect.NOT_AVAILABLE,
            apply_effect_user_hint=_THEME_RESTART_HELP,
            allowed_themes=(),
        )

    try:
        allowed = list_registered_product_themes()
    except Exception:
        allowed = ()

    return ThemeOverlaySnapshot(
        active_gui_id=active_gui_id,
        current_theme_id=current,
        switching_supported=True,
        switching_block_reason=None,
        apply_effect=ThemeApplyEffect.IMMEDIATE,
        apply_effect_user_hint=_THEME_IMMEDIATE_HELP,
        allowed_themes=allowed,
    )


def apply_theme_via_product(active_gui_id: str, theme_id: str) -> ThemeApplyResult:
    """
    Fail-closed Theme-Wechsel: validieren → anwenden → persistieren; bei Persistenzfehler visuell zurücksetzen.
    """
    snap = build_theme_overlay_snapshot(active_gui_id)
    if not snap.switching_supported:
        return ThemeApplyResult(
            ok=False,
            message=snap.switching_block_reason or "Theme switching is not supported for this GUI.",
        )

    tid = (theme_id or "").strip()
    if not tid:
        return ThemeApplyResult(ok=False, message="No theme selected.")

    from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter
    from app.ui_contracts.workspaces.settings_appearance import SettingsAppearancePortError

    adapter = ServiceSettingsAdapter()
    if not adapter.validate_theme_id(tid):
        return ThemeApplyResult(ok=False, message=f"Unknown or unregistered theme: {tid!r}.")

    previous = current_product_theme_id()
    if not apply_product_theme_visual(tid):
        return ThemeApplyResult(
            ok=False,
            message="Theme could not be activated (ThemeManager.set_theme returned false).",
        )

    try:
        adapter.persist_theme_choice(tid)
    except SettingsAppearancePortError as exc:
        apply_product_theme_visual(previous)
        return ThemeApplyResult(ok=False, message=str(exc) or "Could not save theme preference.")
    except Exception as exc:
        apply_product_theme_visual(previous)
        return ThemeApplyResult(ok=False, message=f"Could not save theme preference: {exc}")

    return ThemeApplyResult(ok=True, message=f"Theme set to {tid!r} (saved).")
