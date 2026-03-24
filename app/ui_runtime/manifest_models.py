"""
Theme-Manifest — Datenmodell + JSON-Schema-Validierung.

``schema_version`` Major wird gegen ``SUPPORTED_MANIFEST_SCHEMA_MAJOR`` geprüft.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema

# Nur Major 1 wird in Phase 1 akzeptiert; Minor/Patch sind dokumentativ.
SUPPORTED_MANIFEST_SCHEMA_MAJOR = 1

THEME_MANIFEST_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": True,
    "required": [
        "schema_version",
        "theme_id",
        "display_name",
        "runtime",
        "packs",
        "supported_workspaces",
        "fallback_policy",
        "min_app_compat",
    ],
    "properties": {
        "schema_version": {"type": "string", "pattern": r"^[0-9]+\.[0-9]+$"},
        "theme_id": {"type": "string", "minLength": 1, "pattern": r"^[a-z0-9_]+$"},
        "display_name": {"type": "string", "minLength": 1},
        "runtime": {
            "type": "object",
            "required": ["primary"],
            "properties": {
                "primary": {"type": "string", "enum": ["pyside6_widgets", "qt_quick"]},
                "secondary": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": False,
        },
        "packs": {
            "type": "object",
            "required": ["design", "layout", "icons"],
            "properties": {
                "design": {
                    "type": "object",
                    "required": ["entry"],
                    "properties": {
                        "entry": {"type": "string"},
                        "qss": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": True,
                },
                "layout": {
                    "type": "object",
                    "required": ["entry"],
                    "properties": {"entry": {"type": "string"}},
                    "additionalProperties": True,
                },
                "icons": {
                    "type": "object",
                    "required": ["manifest"],
                    "properties": {
                        "prefix": {"type": "string"},
                        "manifest": {"type": "string"},
                    },
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        },
        "supported_workspaces": {"type": "array", "items": {"type": "string", "minLength": 1}},
        "fallback_policy": {
            "type": "string",
            "enum": [
                "use_builtin_light_default",
                "reject",
                "use_parent_theme_only",
            ],
        },
        "min_app_compat": {"type": "string", "minLength": 1},
        "extends": {"type": ["string", "null"]},
        "capabilities": {"type": "array", "items": {"type": "string"}},
        "asset_version": {"type": ["string", "null"]},
    },
}


@dataclass(frozen=True, slots=True)
class ThemeManifest:
    schema_version: str
    theme_id: str
    display_name: str
    runtime_primary: str
    runtime_secondary: tuple[str, ...]
    packs: dict[str, Any]
    supported_workspaces: tuple[str, ...]
    fallback_policy: str
    min_app_compat: str
    extends: str | None
    capabilities: tuple[str, ...]
    asset_version: str | None
    source_path: Path | None = None

    def resolve_pack_path(self, relative: str) -> Path | None:
        """Löst einen im Manifest relativen Pfad auf (Theme-Root = Verzeichnis des Manifests)."""
        if not self.source_path:
            return None
        base = self.source_path.parent
        p = (base / relative).resolve()
        try:
            p.relative_to(base.resolve())
        except ValueError:
            return None
        return p


def _parse_schema_major(schema_version: str) -> int:
    m = re.match(r"^(\d+)", schema_version.strip())
    if not m:
        raise ValueError(f"Ungültige schema_version: {schema_version!r}")
    return int(m.group(1))


def validate_manifest_dict(data: dict[str, Any]) -> None:
    """
    Wirft ValueError bei Schemafehlern oder nicht unterstützter Major-Version.
    """
    jsonschema.validate(instance=data, schema=THEME_MANIFEST_JSON_SCHEMA)
    major = _parse_schema_major(str(data["schema_version"]))
    if major != SUPPORTED_MANIFEST_SCHEMA_MAJOR:
        raise ValueError(
            f"Manifest schema major {major} wird nicht unterstützt "
            f"(erwartet: {SUPPORTED_MANIFEST_SCHEMA_MAJOR})"
        )


def theme_manifest_from_dict(data: dict[str, Any], *, source_path: Path | None = None) -> ThemeManifest:
    validate_manifest_dict(data)
    runtime = data["runtime"]
    sec = runtime.get("secondary") or []
    caps = data.get("capabilities") or []
    extends = data.get("extends")
    return ThemeManifest(
        schema_version=str(data["schema_version"]),
        theme_id=str(data["theme_id"]),
        display_name=str(data["display_name"]),
        runtime_primary=str(runtime["primary"]),
        runtime_secondary=tuple(str(x) for x in sec),
        packs=dict(data["packs"]),
        supported_workspaces=tuple(str(x) for x in data["supported_workspaces"]),
        fallback_policy=str(data["fallback_policy"]),
        min_app_compat=str(data["min_app_compat"]),
        extends=str(extends) if extends else None,
        capabilities=tuple(str(x) for x in caps),
        asset_version=str(data["asset_version"]) if data.get("asset_version") else None,
        source_path=source_path,
    )
