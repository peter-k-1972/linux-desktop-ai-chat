"""
Zentraler Validator vor Start einer alternativen Qt-Quick-GUI (fail-closed).

Kombiniert Manifest-Parsing, Kompatibilitätslisten und Abgleich mit :class:`GuiDescriptor`.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.application_release_info import (
    APP_RELEASE_VERSION,
    BACKEND_BUNDLE_VERSION,
    BRIDGE_INTERFACE_VERSION,
    UI_CONTRACTS_RELEASE_VERSION,
)
from app.gui_registry import GUI_ID_LIBRARY_QML, GuiDescriptor, get_gui_descriptor
from app.qml_theme_governance import validate_qml_theme_for_repo

logger = logging.getLogger(__name__)


def validate_library_qml_gui_launch_context(
    repo_root: Path,
    *,
    expected_gui_id: str = GUI_ID_LIBRARY_QML,
) -> dict[str, Any]:
    """
    Prüft Manifest + Runtime-Kompatibilität + ``theme_id`` == registrierte ``gui_id``.

    Raises:
        FileNotFoundError, ValueError: bei Verstoß — Aufrufer leitet Fallback ein.
    """
    desc = get_gui_descriptor(expected_gui_id)
    if desc.gui_type != "qt_quick":
        raise ValueError(f"GUI {expected_gui_id!r} is not a qt_quick variant")

    data = validate_qml_theme_for_repo(
        repo_root,
        app_version=APP_RELEASE_VERSION,
        backend_version=BACKEND_BUNDLE_VERSION,
        contract_version=UI_CONTRACTS_RELEASE_VERSION,
        bridge_version=BRIDGE_INTERFACE_VERSION,
    )
    tid = str(data.get("theme_id") or "").strip()
    if tid != expected_gui_id:
        raise ValueError(
            f"theme_id mismatch: manifest has {tid!r}, registry expects {expected_gui_id!r}"
        )
    logger.info(
        "Alternative GUI manifest OK: theme_id=%s theme_version=%s",
        data.get("theme_id"),
        data.get("theme_version"),
    )
    return data


def assert_descriptor_matches_manifest_paths(desc: GuiDescriptor, repo_root: Path) -> None:
    """Prüft, ob ``manifest_path`` relativ zur Repo-Wurzel existiert (falls gesetzt)."""
    if not desc.manifest_path:
        return
    p = (repo_root / desc.manifest_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"GUI manifest missing for {desc.gui_id}: {p}")
