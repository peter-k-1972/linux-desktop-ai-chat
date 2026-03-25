"""
Kompatibilitäts-Metadaten für discoverbare FeatureRegistrare.

Kein SemVer-Framework — nur ein kleiner, expliziter Vertrag für Governance und Checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

# Monoton steigende Plattform-Version (Major.Minor…); einfache lexikografische
# Komponenten-Vergleiche — keine komplexe SemVer-Semantik.
FEATURE_HOST_PLATFORM_VERSION: str = "1"


class FeatureSourceKind(str, Enum):
    """Woher der Registrar geladen wurde (von der Discovery-Pipeline gesetzt, nicht vom Extension-Code)."""

    BUILTIN = "builtin"
    PLUGIN = "plugin"
    EXTENSION = "extension"
    ENTRY_POINT = "entry_point"
    ENV = "env"


@dataclass(frozen=True, slots=True)
class FeatureCompatibility:
    """
    Erweiterungsvertrag: Namen, API-Stufe, Host-Band, Feature- und Gruppen-Beziehungen.

    ``source_kind`` spiegelt die tatsächliche Discovery-Quelle; Aufrufer setzen ihn beim
    Auflösen, nicht allein nach Angabe der Extension.
    """

    feature_name: str
    api_version: str
    min_host_version: Optional[str]
    max_host_version: Optional[str]
    requires_features: tuple[str, ...]
    incompatible_features: tuple[str, ...]
    declared_dependency_groups: tuple[str, ...]
    source_kind: FeatureSourceKind


def resolve_feature_compatibility(
    registrar: Any,
    *,
    source_kind: FeatureSourceKind,
) -> FeatureCompatibility:
    """
    Liefert FeatureCompatibility: optional ``get_feature_compatibility()`` der Extension,
    sonst Synthese aus ``get_descriptor()``.
    """
    desc = registrar.get_descriptor()
    explicit = None
    getter = getattr(registrar, "get_feature_compatibility", None)
    if callable(getter):
        try:
            explicit = getter()
        except Exception:
            explicit = None
    if explicit is not None:
        if not isinstance(explicit, FeatureCompatibility):
            raise TypeError(
                "get_feature_compatibility() muss FeatureCompatibility oder None liefern, "
                f"nicht {type(explicit).__name__}."
            )
        return FeatureCompatibility(
            feature_name=explicit.feature_name,
            api_version=explicit.api_version,
            min_host_version=explicit.min_host_version,
            max_host_version=explicit.max_host_version,
            requires_features=tuple(explicit.requires_features),
            incompatible_features=tuple(explicit.incompatible_features),
            declared_dependency_groups=tuple(explicit.declared_dependency_groups),
            source_kind=source_kind,
        )
    return FeatureCompatibility(
        feature_name=desc.name,
        api_version="1",
        min_host_version=None,
        max_host_version=None,
        requires_features=(),
        incompatible_features=(),
        declared_dependency_groups=tuple(desc.optional_dependencies),
        source_kind=source_kind,
    )


def simple_version_tuple(version: str) -> tuple[Any, ...]:
    parts: list[Any] = []
    for p in version.split("."):
        p = p.strip()
        if p.isdigit():
            parts.append(int(p))
        else:
            parts.append(p)
    return tuple(parts)


def host_version_satisfies(
    host: str,
    min_version: Optional[str],
    max_version: Optional[str],
) -> tuple[bool, Optional[str]]:
    """
    Returns:
        (ok, reason_if_not_ok) — naive Komponenten-Vergleich (int wenn Ziffern, sonst str).
    """
    hk = simple_version_tuple(host)
    if min_version is not None:
        if hk < simple_version_tuple(min_version):
            return False, f"Host-Version {host!r} < min_host_version {min_version!r}"
    if max_version is not None:
        if hk > simple_version_tuple(max_version):
            return False, f"Host-Version {host!r} > max_host_version {max_version!r}"
    return True, None
