"""
Laden und Validierung von ``qml/theme_manifest.json`` (Library QML GUI — Governance).

Kein Ersatz für ``app.ui_runtime.manifest_models.ThemeManifest`` (Widget-Themes).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REQUIRED_TOP_LEVEL_KEYS = (
    "theme_id",
    "theme_name",
    "theme_version",
    "foundation_version",
    "shell_version",
    "bridge_version",
    "domain_versions",
    "compatible_app_versions",
    "compatible_backend_versions",
    "compatible_contract_versions",
    "compatible_bridge_versions",
    "release_status",
)

# Pflicht-Domänen gemäß QML Shell (Nav / Stages).
REQUIRED_DOMAIN_KEYS: frozenset[str] = frozenset(
    {
        "chat",
        "projects",
        "workflows",
        "prompts",
        "agents",
        "deployment",
        "settings",
    }
)


def qml_theme_manifest_path(repo_root: Path) -> Path:
    return (repo_root / "qml" / "theme_manifest.json").resolve()


def load_qml_theme_manifest_dict(repo_root: Path) -> dict[str, Any]:
    path = qml_theme_manifest_path(repo_root)
    if not path.is_file():
        raise FileNotFoundError(f"QML theme manifest missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("theme_manifest.json must contain a JSON object")
    return data


def validate_qml_theme_manifest_shape(data: dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in data]
    if missing:
        raise ValueError(f"theme_manifest.json missing keys: {', '.join(missing)}")
    tv = data.get("theme_version")
    if not tv or not str(tv).strip():
        raise ValueError("theme_version must be non-empty")
    domains = data.get("domain_versions")
    if not isinstance(domains, dict) or not domains:
        raise ValueError("domain_versions must be a non-empty object")
    missing_dom = sorted(REQUIRED_DOMAIN_KEYS - set(domains.keys()))
    if missing_dom:
        raise ValueError(f"domain_versions missing keys: {', '.join(missing_dom)}")
    for k in REQUIRED_DOMAIN_KEYS:
        v = domains.get(k)
        if v is None or not str(v).strip():
            raise ValueError(f"domain_versions[{k!r}] must be non-empty")


def assert_qml_theme_runtime_compatible(
    data: dict[str, Any],
    *,
    app_version: str,
    backend_version: str,
    contract_version: str,
    bridge_version: str,
) -> None:
    """
    Prüft explizite Freigabe-Listen (kein Semver-Range in dieser Phase).

    Args:
        bridge_version: Laufzeitlabel (:data:`app.application_release_info.BRIDGE_INTERFACE_VERSION`).
    """
    validate_qml_theme_manifest_shape(data)

    app_list = data.get("compatible_app_versions")
    if not isinstance(app_list, list) or app_version not in app_list:
        raise ValueError(
            f"App version {app_version!r} not in compatible_app_versions "
            f"(manifest allows {app_list!r})"
        )

    back_list = data.get("compatible_backend_versions")
    if not isinstance(back_list, list) or backend_version not in back_list:
        raise ValueError(
            f"Backend bundle {backend_version!r} not in compatible_backend_versions "
            f"(manifest allows {back_list!r})"
        )

    con_list = data.get("compatible_contract_versions")
    if not isinstance(con_list, list) or contract_version not in con_list:
        raise ValueError(
            f"Contract version {contract_version!r} not in compatible_contract_versions "
            f"(manifest allows {con_list!r})"
        )

    br_list = data.get("compatible_bridge_versions")
    if not isinstance(br_list, list) or bridge_version not in br_list:
        raise ValueError(
            f"Bridge version {bridge_version!r} not in compatible_bridge_versions "
            f"(manifest allows {br_list!r})"
        )


def validate_qml_theme_for_repo(
    repo_root: Path,
    *,
    app_version: str,
    backend_version: str,
    contract_version: str,
    bridge_version: str,
) -> dict[str, Any]:
    """Lädt und validiert das Manifest; gibt die Daten zurück (für Logging/Tests)."""
    data = load_qml_theme_manifest_dict(repo_root)
    assert_qml_theme_runtime_compatible(
        data,
        app_version=app_version,
        backend_version=backend_version,
        contract_version=contract_version,
        bridge_version=bridge_version,
    )
    return data


def log_manifest_summary(data: dict[str, Any]) -> None:
    logger.info(
        "QML theme manifest: id=%s version=%s release_status=%s",
        data.get("theme_id"),
        data.get("theme_version"),
        data.get("release_status"),
    )
