"""
Auflösung der aktiven GUI-Variante (CLI, Umgebung, QSettings).

Speichert kanonische ``gui_id`` (``default_widget_gui`` | ``library_qml_gui``).
"""

from __future__ import annotations

import logging
import os

from app.gui_registry import (
    GUI_ID_DEFAULT_WIDGET,
    GUI_ID_LIBRARY_QML,
    get_default_fallback_gui_id,
    normalize_cli_gui_token,
)

logger = logging.getLogger(__name__)

_QSETTINGS_ORG = "OllamaChat"
_QSETTINGS_APP = "LinuxDesktopChat"

# One-shot: nächster Start erzwingt sicheren Minimalpfad (siehe run_gui_shell / run_qml_shell).
_SAFE_MODE_NEXT_LAUNCH_KEY = "safe_mode_next_launch"
# Hinweis-Banner: Watchdog hat Safe Mode ausgelöst (Overlay-Text bis Nutzer deaktiviert / GUI-Wechsel).
_SAFE_MODE_WATCHDOG_BANNER_KEY = "safe_mode_watchdog_banner"

# Produkt-Standard-Theme (Widget-GUI / AppSettings)
_PRODUCT_DEFAULT_THEME_ID = "light_default"
_PRODUCT_DEFAULT_THEME_LEGACY = "light"


def _normalize_stored_preferred_gui(raw: str | None) -> str:
    """QSettings-Wert → kanonische gui_id (inkl. Legacy ``default`` / ``library_qml``)."""
    v = (raw or "").strip().lower()
    if not v:
        return get_default_fallback_gui_id()
    if v == GUI_ID_DEFAULT_WIDGET.lower():
        return GUI_ID_DEFAULT_WIDGET
    if v == GUI_ID_LIBRARY_QML.lower():
        return GUI_ID_LIBRARY_QML
    mapped = normalize_cli_gui_token(v)
    if mapped is not None:
        return mapped
    return get_default_fallback_gui_id()


def read_preferred_gui_id_from_qsettings() -> str:
    qs = product_qsettings()
    return _normalize_stored_preferred_gui(str(qs.value("preferred_gui", GUI_ID_DEFAULT_WIDGET) or ""))


def write_preferred_gui_id_to_qsettings(gui_id: str) -> None:
    mapped = normalize_cli_gui_token(gui_id)
    if mapped is None:
        if gui_id in (GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML):
            canonical = gui_id
        else:
            canonical = get_default_fallback_gui_id()
            logger.warning("Unknown preferred_gui %r, persisting fallback %s", gui_id, canonical)
    else:
        canonical = mapped

    qs = product_qsettings()
    qs.setValue("preferred_gui", canonical)
    qs.sync()
    logger.info("preferred_gui persisted: %s", canonical)


def resolve_active_gui_id(*, cli_gui: str | None) -> str:
    """
    Priorität: CLI ``--gui`` > ``LINUX_DESKTOP_CHAT_GUI`` > QSettings ``preferred_gui`` > Fallback.
    """
    if cli_gui is not None:
        mapped = normalize_cli_gui_token(cli_gui)
        if mapped is not None:
            return mapped
        if cli_gui in (GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML):
            return cli_gui
        return get_default_fallback_gui_id()

    env_raw = (os.environ.get("LINUX_DESKTOP_CHAT_GUI") or "").strip()
    if env_raw:
        mapped = normalize_cli_gui_token(env_raw)
        if mapped is not None:
            return mapped

    return read_preferred_gui_id_from_qsettings()


# --- Abwärtskompatibel: alte Funktionsnamen aus Phase 2 ---
def normalize_gui_registry_key(raw: str | None) -> str:
    """DEPRECATED: Nutze ``normalize_cli_gui_token`` + gui_id. Mappt auf Legacy-Keys für alte Aufrufer."""
    gid = normalize_cli_gui_token(raw)
    if gid == GUI_ID_LIBRARY_QML:
        return "library_qml"
    return "default"


def write_preferred_gui_to_qsettings(key: str) -> None:
    """DEPRECATED: delegiert zu ``write_preferred_gui_id_to_qsettings``."""
    write_preferred_gui_id_to_qsettings(key)


def read_preferred_gui_from_qsettings() -> str:
    """DEPRECATED: gibt Legacy-Key ``default``/``library_qml`` zurück."""
    gid = read_preferred_gui_id_from_qsettings()
    return "library_qml" if gid == GUI_ID_LIBRARY_QML else "default"


def resolve_gui_registry_key(*, cli_gui: str | None) -> str:
    """DEPRECATED: nutze ``resolve_active_gui_id``."""
    gid = resolve_active_gui_id(cli_gui=cli_gui)
    return "library_qml" if gid == GUI_ID_LIBRARY_QML else "default"


def ensure_qsettings_core_application() -> None:
    """
    Setzt Org/App für QSettings, bevor eine QApplication existiert (CLI-/Watchdog-Pfade).

    Kein eigenes QCoreApplication: sonst kollidiert der spätere ``QApplication``-Start.
    """
    try:
        from PySide6.QtCore import QCoreApplication

        QCoreApplication.setOrganizationName(_QSETTINGS_ORG)
        QCoreApplication.setApplicationName(_QSETTINGS_APP)
    except Exception:
        pass


def product_qsettings():
    """Zentrale QSettings-Instanz für Produkt-Org/App (auch vor ``QApplication``)."""
    from PySide6.QtCore import QSettings

    ensure_qsettings_core_application()
    return QSettings(_QSETTINGS_ORG, _QSETTINGS_APP)


def _qsettings_instance():
    return product_qsettings()


def _coerce_bool_qsettings(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ("true", "1", "yes", "on")


def read_safe_mode_next_launch_pending() -> bool:
    """True wenn Safe-Mode für den nächsten Start geplant ist (Flag noch gesetzt)."""
    try:
        qs = _qsettings_instance()
        return _coerce_bool_qsettings(qs.value(_SAFE_MODE_NEXT_LAUNCH_KEY, False))
    except Exception:
        return False


def write_safe_mode_next_launch_flag(enabled: bool) -> None:
    """Setzt oder löscht das One-Shot-Safe-Mode-Flag."""
    try:
        qs = _qsettings_instance()
        if enabled:
            qs.setValue(_SAFE_MODE_NEXT_LAUNCH_KEY, True)
        else:
            qs.remove(_SAFE_MODE_NEXT_LAUNCH_KEY)
        qs.sync()
    except Exception:
        pass


def read_safe_mode_watchdog_banner() -> bool:
    """
    True wenn die laufende bzw. letzte Safe-Mode-Session vom GUI-Watchdog stammt
    (Overlay-Hinweis bis Deaktivierung / GUI-Wechsel zur alternativen GUI).
    """
    try:
        qs = _qsettings_instance()
        return _coerce_bool_qsettings(qs.value(_SAFE_MODE_WATCHDOG_BANNER_KEY, False))
    except Exception:
        return False


def write_safe_mode_watchdog_banner(enabled: bool) -> None:
    try:
        qs = _qsettings_instance()
        if enabled:
            qs.setValue(_SAFE_MODE_WATCHDOG_BANNER_KEY, True)
        else:
            qs.remove(_SAFE_MODE_WATCHDOG_BANNER_KEY)
        qs.sync()
    except Exception:
        pass


def consume_safe_mode_next_launch() -> bool:
    """
    One-shot: war das Flag gesetzt, wird es entfernt und True zurückgegeben.

    Muss beim Produktstart genau einmal ausgewertet werden.
    """
    try:
        qs = _qsettings_instance()
        if not _coerce_bool_qsettings(qs.value(_SAFE_MODE_NEXT_LAUNCH_KEY, False)):
            return False
        qs.remove(_SAFE_MODE_NEXT_LAUNCH_KEY)
        qs.sync()
        logger.info("safe_mode_next_launch consumed (one-shot)")
        return True
    except Exception:
        return False


def write_product_theme_defaults_to_qsettings() -> None:
    """Persistiert kanonisches Standard-Theme (theme_id + Legacy-Bucket)."""
    qs = _qsettings_instance()
    qs.setValue("theme_id", _PRODUCT_DEFAULT_THEME_ID)
    qs.setValue("theme", _PRODUCT_DEFAULT_THEME_LEGACY)
    qs.sync()
    logger.info(
        "product theme defaults written to QSettings: theme_id=%s",
        _PRODUCT_DEFAULT_THEME_ID,
    )


def write_product_theme_id_to_qsettings(theme_id: str) -> None:
    """
    Persistiert eine kanonische ``theme_id`` + passenden Legacy-``theme``-Bucket.

    Unbekannte IDs werden auf ``light_default`` normalisiert (fail-closed, konsistent mit AppSettings).
    """
    from app.core.config.builtin_theme_ids import BUILTIN_THEME_IDS
    from app.gui.themes.theme_id_utils import is_registered_theme_id, theme_id_to_legacy_light_dark

    tid = (theme_id or "").strip() or _PRODUCT_DEFAULT_THEME_ID
    if tid not in BUILTIN_THEME_IDS:
        try:
            if not is_registered_theme_id(tid):
                tid = _PRODUCT_DEFAULT_THEME_ID
        except Exception:
            tid = _PRODUCT_DEFAULT_THEME_ID
    legacy = theme_id_to_legacy_light_dark(tid)
    qs = _qsettings_instance()
    qs.setValue("theme_id", tid)
    qs.setValue("theme", legacy)
    qs.sync()
    logger.info("product theme_id persisted: %s (legacy bucket %s)", tid, legacy)


def argv_has_long_option(argv: list[str], long_opt: str) -> bool:
    """True bei ``--opt`` oder ``--opt=value`` in ``argv`` (ab Index 1)."""
    prefix = long_opt + "="
    for a in argv[1:]:
        if a == long_opt or a.startswith(prefix):
            return True
    return False
