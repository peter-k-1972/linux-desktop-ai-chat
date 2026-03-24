"""
Registry registrierter GUI-Varianten (kanonische ``gui_id`` + CLI-Aliase).

Wird von ``run_gui_shell`` für ``--gui``, Umgebungsvariable und QSettings genutzt.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from app.gui_capabilities import (
    CAPABILITIES_DEFAULT_WIDGET_GUI,
    CAPABILITIES_LIBRARY_QML_GUI,
    GuiCapabilities,
)

# Kanonische GUI-IDs (auch in ``qml/theme_manifest.json`` theme_id für QML).
GUI_ID_DEFAULT_WIDGET: Final[str] = "default_widget_gui"
GUI_ID_LIBRARY_QML: Final[str] = "library_qml_gui"


@dataclass(frozen=True, slots=True)
class GuiDescriptor:
    """Startbare GUI-Zeile — ein Eintrag pro registrierter Alternative / Standard."""

    gui_id: str
    display_name: str
    gui_type: str
    entrypoint: str
    manifest_path: str | None
    capabilities: GuiCapabilities
    is_default_fallback: bool = False


# Primärindex: gui_id → Deskriptor
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

# CLI / Env / Legacy: Alias → kanonische gui_id
GUI_CLI_ALIASES: Final[dict[str, str]] = {
    "default": GUI_ID_DEFAULT_WIDGET,
    "default_widget_gui": GUI_ID_DEFAULT_WIDGET,
    "widget": GUI_ID_DEFAULT_WIDGET,
    "library_qml": GUI_ID_LIBRARY_QML,
    "library_qml_gui": GUI_ID_LIBRARY_QML,
    "qml": GUI_ID_LIBRARY_QML,
}


def normalize_cli_gui_token(raw: str | None) -> str | None:
    """
    Mappt einen CLI-/Config-String auf eine kanonische ``gui_id``.

    Returns:
        gui_id oder ``None`` wenn unbekannt / leer.
    """
    if raw is None:
        return None
    key = (raw or "").strip().lower()
    if not key:
        return None
    return GUI_CLI_ALIASES.get(key)


def list_valid_gui_cli_tokens() -> tuple[str, ...]:
    """Alle akzeptierten ``--gui``-/Env-Strings (sortiert, ohne Duplikat gui_id)."""
    return tuple(sorted(set(GUI_CLI_ALIASES.keys())))


def get_gui_descriptor(gui_id: str) -> GuiDescriptor:
    if gui_id not in REGISTERED_GUIS_BY_ID:
        raise KeyError(f"Unknown gui_id: {gui_id!r}")
    return REGISTERED_GUIS_BY_ID[gui_id]


def get_default_fallback_gui_id() -> str:
    for d in REGISTERED_GUIS_BY_ID.values():
        if d.is_default_fallback:
            return d.gui_id
    return GUI_ID_DEFAULT_WIDGET


def list_registered_gui_ids() -> tuple[str, ...]:
    return tuple(sorted(REGISTERED_GUIS_BY_ID.keys()))


def resolve_repo_root() -> Path:
    """Repo-Wurzel (Verzeichnis mit ``run_gui_shell.py``)."""
    return Path(__file__).resolve().parents[1]


def resolve_user_gui_choice(token: str) -> str | None:
    """
    Löst CLI-/User-String auf ``gui_id`` auf.

    Akzeptiert Aliase (``default``, ``library_qml_gui``, …) und exakte ``gui_id``.
    """
    raw = (token or "").strip()
    if not raw:
        return None
    by_alias = normalize_cli_gui_token(raw)
    if by_alias is not None:
        return by_alias
    if raw in REGISTERED_GUIS_BY_ID:
        return raw
    return None
