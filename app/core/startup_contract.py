"""
Kanonischer Produkt-Startup-/Theme-Contract.

Diese API bündelt die minimale, extrahierbare Produktfläche für:
- GUI-Registry und Capabilities
- QSettings-basierte GUI-/Theme-Präferenzen
- Safe-Mode-/Watchdog-Flags
- Produkt-Theme-Metadaten

Keine Qt-Widget-Typen, keine Shell-spezifischen Objekte.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Final

logger = logging.getLogger(__name__)

GUI_ID_DEFAULT_WIDGET: Final[str] = "default_widget_gui"
GUI_ID_LIBRARY_QML: Final[str] = "library_qml_gui"

KNOWN_GUI_CAPABILITY_NAMES: Final[tuple[str, ...]] = (
    "supports_chat",
    "supports_projects",
    "supports_workflows",
    "supports_prompts",
    "supports_agents",
    "supports_deployment",
    "supports_settings",
    "supports_theme_switching",
    "supports_command_palette",
    "supports_safe_mode_actions",
)

_QSETTINGS_ORG = "OllamaChat"
_QSETTINGS_APP = "LinuxDesktopChat"
_SAFE_MODE_NEXT_LAUNCH_KEY = "safe_mode_next_launch"
_SAFE_MODE_WATCHDOG_BANNER_KEY = "safe_mode_watchdog_banner"
_PRODUCT_DEFAULT_THEME_ID = "light_default"
_PRODUCT_DEFAULT_THEME_LEGACY = "light"


@dataclass(frozen=True, slots=True)
class GuiCapabilities:
    supports_chat: bool
    supports_projects: bool
    supports_workflows: bool
    supports_prompts: bool
    supports_agents: bool
    supports_deployment: bool
    supports_settings: bool
    supports_theme_switching: bool
    supports_command_palette: bool
    supports_safe_mode_actions: bool


@dataclass(frozen=True, slots=True)
class GuiDescriptor:
    """Startbare GUI-Variante mit produktrelevanter Metadatenfläche."""

    gui_id: str
    display_name: str
    gui_type: str
    entrypoint: str
    manifest_path: str | None
    capabilities: GuiCapabilities
    is_default_fallback: bool = False


CAPABILITIES_DEFAULT_WIDGET_GUI: Final[GuiCapabilities] = GuiCapabilities(
    supports_chat=True,
    supports_projects=True,
    supports_workflows=True,
    supports_prompts=True,
    supports_agents=True,
    supports_deployment=True,
    supports_settings=True,
    supports_theme_switching=True,
    supports_command_palette=True,
    supports_safe_mode_actions=False,
)

CAPABILITIES_LIBRARY_QML_GUI: Final[GuiCapabilities] = GuiCapabilities(
    supports_chat=True,
    supports_projects=True,
    supports_workflows=True,
    supports_prompts=True,
    supports_agents=True,
    supports_deployment=True,
    supports_settings=True,
    supports_theme_switching=False,
    supports_command_palette=False,
    supports_safe_mode_actions=False,
)

CANONICAL_GUI_CAPABILITIES: Final[dict[str, GuiCapabilities]] = {
    GUI_ID_DEFAULT_WIDGET: CAPABILITIES_DEFAULT_WIDGET_GUI,
    GUI_ID_LIBRARY_QML: CAPABILITIES_LIBRARY_QML_GUI,
}

REGISTERED_GUIS_BY_ID: Final[dict[str, GuiDescriptor]] = {
    GUI_ID_DEFAULT_WIDGET: GuiDescriptor(
        gui_id=GUI_ID_DEFAULT_WIDGET,
        display_name="Default Widget GUI",
        gui_type="pyside6",
        entrypoint="run_gui_shell.py",
        manifest_path=None,
        capabilities=CAPABILITIES_DEFAULT_WIDGET_GUI,
        is_default_fallback=True,
    ),
    GUI_ID_LIBRARY_QML: GuiDescriptor(
        gui_id=GUI_ID_LIBRARY_QML,
        display_name="Library QML GUI",
        gui_type="qt_quick",
        entrypoint="run_qml_shell.py",
        manifest_path="qml/theme_manifest.json",
        capabilities=CAPABILITIES_LIBRARY_QML_GUI,
        is_default_fallback=False,
    ),
}

GUI_CLI_ALIASES: Final[dict[str, str]] = {
    "default": GUI_ID_DEFAULT_WIDGET,
    "default_widget_gui": GUI_ID_DEFAULT_WIDGET,
    "widget": GUI_ID_DEFAULT_WIDGET,
    "library_qml": GUI_ID_LIBRARY_QML,
    "library_qml_gui": GUI_ID_LIBRARY_QML,
    "qml": GUI_ID_LIBRARY_QML,
}


def normalize_cli_gui_token(raw: str | None) -> str | None:
    if raw is None:
        return None
    key = (raw or "").strip().lower()
    if not key:
        return None
    return GUI_CLI_ALIASES.get(key)


def list_valid_gui_cli_tokens() -> tuple[str, ...]:
    return tuple(sorted(set(GUI_CLI_ALIASES.keys())))


def get_gui_descriptor(gui_id: str) -> GuiDescriptor:
    if gui_id not in REGISTERED_GUIS_BY_ID:
        raise KeyError(f"Unknown gui_id: {gui_id!r}")
    return REGISTERED_GUIS_BY_ID[gui_id]


def get_default_fallback_gui_id() -> str:
    for desc in REGISTERED_GUIS_BY_ID.values():
        if desc.is_default_fallback:
            return desc.gui_id
    return GUI_ID_DEFAULT_WIDGET


def list_registered_gui_ids() -> tuple[str, ...]:
    return tuple(sorted(REGISTERED_GUIS_BY_ID.keys()))


def resolve_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_user_gui_choice(token: str) -> str | None:
    raw = (token or "").strip()
    if not raw:
        return None
    by_alias = normalize_cli_gui_token(raw)
    if by_alias is not None:
        return by_alias
    if raw in REGISTERED_GUIS_BY_ID:
        return raw
    return None


def gui_supports(gui_id: str, capability: str) -> bool:
    if capability not in KNOWN_GUI_CAPABILITY_NAMES:
        raise ValueError(f"Unknown GUI capability: {capability!r}")
    caps = get_gui_descriptor(gui_id).capabilities
    return bool(getattr(caps, capability))


def get_capabilities_for_gui_id(gui_id: str) -> GuiCapabilities:
    return get_gui_descriptor(gui_id).capabilities


def validate_registered_gui_capabilities(registry: Mapping[str, object]) -> None:
    for gui_id, desc in registry.items():
        expected = CANONICAL_GUI_CAPABILITIES.get(gui_id)
        if expected is None:
            continue
        caps = getattr(desc, "capabilities", None)
        if caps is None:
            raise ValueError(f"GuiDescriptor for {gui_id!r} missing capabilities")
        if caps != expected:
            raise ValueError(
                f"Capabilities drift for {gui_id!r}: registry has {caps!r}, "
                f"canonical is {expected!r}"
            )


def _normalize_stored_preferred_gui(raw: str | None) -> str:
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


def ensure_qsettings_core_application() -> None:
    try:
        from PySide6.QtCore import QCoreApplication

        QCoreApplication.setOrganizationName(_QSETTINGS_ORG)
        QCoreApplication.setApplicationName(_QSETTINGS_APP)
    except Exception:
        pass


def product_qsettings():
    from PySide6.QtCore import QSettings

    ensure_qsettings_core_application()
    return QSettings(_QSETTINGS_ORG, _QSETTINGS_APP)


def _qsettings_instance():
    return product_qsettings()


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


def normalize_gui_registry_key(raw: str | None) -> str:
    gid = normalize_cli_gui_token(raw)
    if gid == GUI_ID_LIBRARY_QML:
        return "library_qml"
    return "default"


def write_preferred_gui_to_qsettings(key: str) -> None:
    write_preferred_gui_id_to_qsettings(key)


def read_preferred_gui_from_qsettings() -> str:
    gid = read_preferred_gui_id_from_qsettings()
    return "library_qml" if gid == GUI_ID_LIBRARY_QML else "default"


def resolve_gui_registry_key(*, cli_gui: str | None) -> str:
    gid = resolve_active_gui_id(cli_gui=cli_gui)
    return "library_qml" if gid == GUI_ID_LIBRARY_QML else "default"


def _coerce_bool_qsettings(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ("true", "1", "yes", "on")


def read_safe_mode_next_launch_pending() -> bool:
    try:
        qs = _qsettings_instance()
        return _coerce_bool_qsettings(qs.value(_SAFE_MODE_NEXT_LAUNCH_KEY, False))
    except Exception:
        return False


def write_safe_mode_next_launch_flag(enabled: bool) -> None:
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
    qs = _qsettings_instance()
    qs.setValue("theme_id", _PRODUCT_DEFAULT_THEME_ID)
    qs.setValue("theme", _PRODUCT_DEFAULT_THEME_LEGACY)
    qs.sync()
    logger.info(
        "product theme defaults written to QSettings: theme_id=%s",
        _PRODUCT_DEFAULT_THEME_ID,
    )


def list_registered_product_themes() -> tuple[tuple[str, str], ...]:
    try:
        get_theme_manager = getattr(import_module("app.gui.themes"), "get_theme_manager")
        return tuple((tid, name) for tid, name in get_theme_manager().list_themes())
    except Exception:
        return ()


def current_product_theme_id() -> str:
    try:
        get_theme_manager = getattr(import_module("app.gui.themes"), "get_theme_manager")
        tid = (get_theme_manager().get_current_id() or "").strip()
        return tid or _PRODUCT_DEFAULT_THEME_ID
    except Exception:
        return _PRODUCT_DEFAULT_THEME_ID


def product_theme_id_registered(theme_id: str) -> bool:
    from app.core.config.builtin_theme_ids import BUILTIN_THEME_IDS

    tid = (theme_id or "").strip()
    if not tid:
        return False
    if tid in BUILTIN_THEME_IDS:
        return True
    try:
        is_registered_theme_id = getattr(
            import_module("app.gui.themes.theme_id_utils"),
            "is_registered_theme_id",
        )
        return bool(is_registered_theme_id(tid))
    except Exception:
        return False


def product_theme_id_to_legacy_bucket(theme_id: str) -> str:
    try:
        theme_id_to_legacy_light_dark = getattr(
            import_module("app.gui.themes.theme_id_utils"),
            "theme_id_to_legacy_light_dark",
        )
        tid = (theme_id or "").strip() or _PRODUCT_DEFAULT_THEME_ID
        return theme_id_to_legacy_light_dark(tid)
    except Exception:
        return _PRODUCT_DEFAULT_THEME_LEGACY


def apply_product_theme_visual(theme_id: str) -> bool:
    try:
        get_theme_manager = getattr(import_module("app.gui.themes"), "get_theme_manager")
        return bool(get_theme_manager().set_theme(theme_id))
    except Exception:
        return False


def write_product_theme_id_to_qsettings(theme_id: str) -> None:
    tid = (theme_id or "").strip() or _PRODUCT_DEFAULT_THEME_ID
    if not product_theme_id_registered(tid):
        tid = _PRODUCT_DEFAULT_THEME_ID
    legacy = product_theme_id_to_legacy_bucket(tid)
    qs = _qsettings_instance()
    qs.setValue("theme_id", tid)
    qs.setValue("theme", legacy)
    qs.sync()
    logger.info("product theme_id persisted: %s (legacy bucket %s)", tid, legacy)


def argv_has_long_option(argv: list[str], long_opt: str) -> bool:
    prefix = long_opt + "="
    for arg in argv[1:]:
        if arg == long_opt or arg.startswith(prefix):
            return True
    return False


__all__ = [
    "CANONICAL_GUI_CAPABILITIES",
    "CAPABILITIES_DEFAULT_WIDGET_GUI",
    "CAPABILITIES_LIBRARY_QML_GUI",
    "GUI_CLI_ALIASES",
    "GUI_ID_DEFAULT_WIDGET",
    "GUI_ID_LIBRARY_QML",
    "GuiCapabilities",
    "GuiDescriptor",
    "KNOWN_GUI_CAPABILITY_NAMES",
    "REGISTERED_GUIS_BY_ID",
    "apply_product_theme_visual",
    "argv_has_long_option",
    "consume_safe_mode_next_launch",
    "current_product_theme_id",
    "ensure_qsettings_core_application",
    "get_capabilities_for_gui_id",
    "get_default_fallback_gui_id",
    "get_gui_descriptor",
    "gui_supports",
    "list_registered_gui_ids",
    "list_registered_product_themes",
    "list_valid_gui_cli_tokens",
    "normalize_cli_gui_token",
    "normalize_gui_registry_key",
    "product_qsettings",
    "product_theme_id_registered",
    "product_theme_id_to_legacy_bucket",
    "read_preferred_gui_from_qsettings",
    "read_preferred_gui_id_from_qsettings",
    "read_safe_mode_next_launch_pending",
    "read_safe_mode_watchdog_banner",
    "resolve_active_gui_id",
    "resolve_gui_registry_key",
    "resolve_repo_root",
    "resolve_user_gui_choice",
    "validate_registered_gui_capabilities",
    "write_preferred_gui_id_to_qsettings",
    "write_preferred_gui_to_qsettings",
    "write_product_theme_defaults_to_qsettings",
    "write_product_theme_id_to_qsettings",
    "write_safe_mode_next_launch_flag",
    "write_safe_mode_watchdog_banner",
]
