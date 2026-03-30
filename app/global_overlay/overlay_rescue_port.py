"""
Produktweite Rescue-Aktionen (Slice 4) — kein Domänencode, fail-closed.

Persistenz über ``app.core.startup_contract`` / ``ServiceSettingsAdapter``.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.startup_contract import (
    GUI_ID_DEFAULT_WIDGET,
    get_default_fallback_gui_id,
    apply_product_theme_visual,
    product_theme_id_to_legacy_bucket,
    read_preferred_gui_id_from_qsettings,
    write_preferred_gui_id_to_qsettings,
    write_product_theme_defaults_to_qsettings,
    write_safe_mode_next_launch_flag,
    write_safe_mode_watchdog_banner,
)

_PRODUCT_DEFAULT_THEME_ID = "light_default"


@dataclass(frozen=True, slots=True)
class RescueResult:
    ok: bool
    message: str
    relaunch_scheduled: bool = False


def rescue_revert_to_default_gui_relaunch(active_gui_id: str) -> RescueResult:
    """Setzt bevorzugte GUI auf Fallback und relauncht (Slice 3)."""
    from app.global_overlay.overlay_gui_port import revert_to_default_gui_via_product

    r = revert_to_default_gui_via_product(active_gui_id)
    return RescueResult(ok=r.ok, message=r.message, relaunch_scheduled=r.relaunch_scheduled)


def rescue_reset_preferred_gui_only() -> RescueResult:
    """
    Setzt ``preferred_gui`` auf den Registry-Default — **ohne** Relaunch.

    Synchronisiert QSettings und, falls vorhanden, ``AppSettings`` + ``save()``.
    """
    try:
        fallback = get_default_fallback_gui_id()
        write_preferred_gui_id_to_qsettings(fallback)
        try:
            from app.services.infrastructure import get_infrastructure

            infra = get_infrastructure()
            infra.settings.preferred_gui = fallback
            infra.settings.save()
        except Exception:
            pass
        return RescueResult(
            True,
            f"Preferred GUI reset to {fallback!r} (saved). Next start uses this unless CLI/env overrides.",
        )
    except Exception as exc:
        return RescueResult(False, f"Could not reset preferred GUI: {exc}")


def rescue_reset_preferred_theme_only(active_gui_id: str) -> RescueResult:
    """
    Setzt persistiertes Theme auf Produkt-Default (``light_default``).

    Schreibt QSettings; bei laufender Infrastruktur AppSettings + ThemeManager (Widget-Pfad).
    """
    try:
        write_product_theme_defaults_to_qsettings()
        try:
            from app.services.infrastructure import get_infrastructure

            infra = get_infrastructure()
            infra.settings.theme_id = _PRODUCT_DEFAULT_THEME_ID
            infra.settings.theme = product_theme_id_to_legacy_bucket(_PRODUCT_DEFAULT_THEME_ID)
            infra.settings.save()
        except Exception:
            pass
        try:
            if active_gui_id == GUI_ID_DEFAULT_WIDGET:
                apply_product_theme_visual(_PRODUCT_DEFAULT_THEME_ID)
        except Exception:
            pass
        return RescueResult(
            True,
            f"Preferred theme reset to {_PRODUCT_DEFAULT_THEME_ID!r} (saved). "
            "Widget GUI applies immediately if active.",
        )
    except Exception as exc:
        return RescueResult(False, f"Could not reset preferred theme: {exc}")


def rescue_disable_safe_mode_watchdog() -> RescueResult:
    """
    Entfernt Safe-Mode-Planung, Watchdog-Banner und persistierte Fehlerhistorie.

    Kein Relaunch — nur Zustand bereinigen (Nutzer bestätigt im Emergency-Overlay).
    """
    try:
        from app.global_overlay.gui_launch_watchdog import clear_watchdog_failure_persistence

        write_safe_mode_next_launch_flag(False)
        write_safe_mode_watchdog_banner(False)
        clear_watchdog_failure_persistence()
        return RescueResult(
            True,
            "Safe mode scheduling cleared, watchdog failure history reset, recovery banner dismissed.",
        )
    except Exception as exc:
        return RescueResult(False, f"Could not disable safe mode state: {exc}")


def rescue_enable_safe_mode_next_launch() -> RescueResult:
    """One-Shot: nächster Start wendet Minimalpfad an (siehe ``consume_safe_mode_next_launch``)."""
    try:
        write_safe_mode_next_launch_flag(True)
        return RescueResult(
            True,
            "Safe mode enabled for the **next launch only** (one-shot): "
            "default widget GUI and default theme unless you pass explicit --gui / --theme.",
        )
    except Exception as exc:
        return RescueResult(False, f"Could not enable safe mode flag: {exc}")


def rescue_restart_application(active_gui_id: str) -> RescueResult:
    """
    Relaunch über ``run_gui_shell.py`` mit aktuell gespeicherter Präferenz (keine Änderung davor).
    """
    from app.global_overlay.overlay_gui_port import relaunch_via_run_gui_shell
    try:
        gid = read_preferred_gui_id_from_qsettings()
    except Exception:
        gid = get_default_fallback_gui_id()
    if not relaunch_via_run_gui_shell(gid):
        return RescueResult(False, "Could not start run_gui_shell.py for restart.")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is not None:
        app.quit()
    return RescueResult(True, f"Restarting via run_gui_shell.py with preferred GUI {gid!r} …", True)
