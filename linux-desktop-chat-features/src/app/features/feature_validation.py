"""
Zentrale Validierung für FeatureDescriptor, FeatureCompatibility und FeatureRegistrar.

Discovery nutzt diese Funktionen fail-soft (Fehler → Skip + Log, keine harte App-Abbrüche).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, FrozenSet, Iterable, Optional

from app.features.compatibility import (
    FEATURE_HOST_PLATFORM_VERSION,
    FeatureCompatibility,
    FeatureSourceKind,
    host_version_satisfies,
    resolve_feature_compatibility,
    simple_version_tuple,
)
from app.features.descriptors import FeatureDescriptor
from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES

_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$")


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_feature_name(name: str, source_kind: FeatureSourceKind) -> ValidationResult:
    """Verbindliche Namensregeln; Builtin-Referenzmenge vs. erweiternde Quellen."""
    res = ValidationResult()
    if not name or not str(name).strip():
        res.errors.append("Feature-Name fehlt oder ist leer.")
        return res
    if not _NAME_RE.match(name):
        res.errors.append(
            f"Feature-Name {name!r} entspricht nicht dem Muster "
            f"(snake_case-Segmente, optional mit Punkt-Namespace: vendor.feature)."
        )
        return res
    if source_kind is FeatureSourceKind.BUILTIN:
        if name not in ALL_BUILTIN_FEATURE_NAMES:
            res.errors.append(
                f"Builtin-Feature {name!r} ist nicht im Katalog ALL_BUILTIN_FEATURE_NAMES."
            )
    else:
        if name in ALL_BUILTIN_FEATURE_NAMES:
            res.errors.append(
                f"Name {name!r} ist für Produkt-Builtins reserviert — Erweiterungen "
                f"dürfen ihn nicht verwenden (Quelle: {source_kind.value})."
            )
        elif not (name.startswith("plugin_") or name.startswith("ext_") or "." in name):
            res.errors.append(
                f"Erweiterungs-Feature {name!r} muss mit plugin_ oder ext_ beginnen "
                f"oder einen Punkt-Namespace enthalten (z. B. acme.mein_feature)."
            )
    return res


def validate_feature_descriptor(descriptor: FeatureDescriptor) -> ValidationResult:
    """Pflichtmetadaten des Deskriptors (ohne Quellen-Herkunft)."""
    res = ValidationResult()
    if not descriptor.description or not str(descriptor.description).strip():
        res.errors.append(f"Feature {descriptor.name!r}: description darf nicht leer sein.")
    return res


def validate_feature_compatibility(
    compatibility: FeatureCompatibility,
    *,
    descriptor_name: str,
    known_dependency_group_names: FrozenSet[str],
    host_version: str = FEATURE_HOST_PLATFORM_VERSION,
) -> ValidationResult:
    """Kompatibilitätsblock: Konsistenz mit Deskriptor, Host-Band, Dependency-Gruppen."""
    res = ValidationResult()
    if compatibility.feature_name != descriptor_name:
        res.errors.append(
            f"feature_name {compatibility.feature_name!r} weicht von Deskriptor.name "
            f"{descriptor_name!r} ab."
        )
    if not str(compatibility.api_version).strip():
        res.errors.append("api_version darf nicht leer sein.")
    if compatibility.min_host_version is not None and compatibility.max_host_version is not None:
        if simple_version_tuple(compatibility.min_host_version) > simple_version_tuple(
            compatibility.max_host_version
        ):
            res.errors.append(
                f"min_host_version {compatibility.min_host_version!r} > "
                f"max_host_version {compatibility.max_host_version!r}."
            )
    ok_host, reason = host_version_satisfies(
        host_version,
        compatibility.min_host_version,
        compatibility.max_host_version,
    )
    if not ok_host and reason:
        res.errors.append(reason)
    for g in compatibility.declared_dependency_groups:
        if g not in known_dependency_group_names:
            res.errors.append(f"Unbekannte Dependency-Gruppe {g!r} (nicht im DependencyGroupRegistry).")
    if compatibility.feature_name in compatibility.incompatible_features:
        res.errors.append("incompatible_features darf den eigenen Namen nicht enthalten.")
    return res


def validate_feature_registrar(
    registrar: Any,
    *,
    source_kind: FeatureSourceKind,
    known_dependency_group_names: FrozenSet[str],
    accepted_feature_names: FrozenSet[str],
    host_version: str = FEATURE_HOST_PLATFORM_VERSION,
) -> ValidationResult:
    """
    Gesamtcheck für einen Registrar vor Registrierung.

    ``accepted_feature_names``: bereits gültige Namen (Builtins + zuvor akzeptierte Extensions),
    für ``requires_features``.
    """
    res = ValidationResult()
    if not callable(getattr(registrar, "get_descriptor", None)):
        res.errors.append("Registrar: get_descriptor fehlt oder ist nicht aufrufbar.")
        return res
    try:
        desc = registrar.get_descriptor()
    except Exception as exc:  # noqa: BLE001
        res.errors.append(f"get_descriptor() fehlgeschlagen: {exc}")
        return res
    if not isinstance(desc, FeatureDescriptor):
        res.errors.append("get_descriptor() muss FeatureDescriptor liefern.")
        return res

    nres = validate_feature_name(desc.name, source_kind)
    res.errors.extend(nres.errors)
    res.warnings.extend(nres.warnings)
    dres = validate_feature_descriptor(desc)
    res.errors.extend(dres.errors)
    res.warnings.extend(dres.warnings)

    try:
        compat = resolve_feature_compatibility(registrar, source_kind=source_kind)
    except Exception as exc:  # noqa: BLE001
        res.errors.append(f"Kompatibilität nicht auflösbar: {exc}")
        return res

    cres = validate_feature_compatibility(
        compat,
        descriptor_name=desc.name,
        known_dependency_group_names=known_dependency_group_names,
        host_version=host_version,
    )
    res.errors.extend(cres.errors)
    res.warnings.extend(cres.warnings)

    missing_req = [f for f in compat.requires_features if f not in accepted_feature_names]
    if missing_req:
        res.errors.append(
            "requires_features verweist auf unbekannte Features: "
            + ", ".join(repr(x) for x in missing_req)
            + f" (bekannt: {sorted(accepted_feature_names)})"
        )

    return res


def plan_registration_order(
    items: Iterable[tuple[Any, FeatureSourceKind]],
    *,
    known_dependency_group_names: FrozenSet[str],
    host_version: str = FEATURE_HOST_PLATFORM_VERSION,
    log: Optional[Any] = None,
) -> list[tuple[Any, FeatureSourceKind]]:
    """
    Filtert und ordnet Registrare: Builtins zuerst, dann Extensions (jeweils Input-Reihenfolge).

    Übersprungene Einträge: ``log`` warning (Fehler); reine Validierungs-Warnungen ebenfalls per Log.
    """
    import logging

    _log = log or logging.getLogger(__name__)
    accepted: list[tuple[Any, FeatureSourceKind]] = []
    names_ok: set[str] = set(ALL_BUILTIN_FEATURE_NAMES)

    bucket_builtin: list[tuple[Any, FeatureSourceKind]] = []
    bucket_rest: list[tuple[Any, FeatureSourceKind]] = []
    for reg, sk in items:
        if sk is FeatureSourceKind.BUILTIN:
            bucket_builtin.append((reg, sk))
        else:
            bucket_rest.append((reg, sk))

    registered_names: set[str] = set()

    def _try_one(reg: Any, sk: FeatureSourceKind) -> None:
        nonlocal names_ok
        try:
            desc = reg.get_descriptor()
        except Exception as exc:  # noqa: BLE001
            _log.warning(
                "Feature-Governance: Registrar übersprungen (%s): get_descriptor: %s",
                sk.value,
                exc,
            )
            return
        desc_name = desc.name
        if desc_name in registered_names:
            _log.warning(
                "Feature-Governance: Registrar %r übersprungen (%s): Duplikat im Discovery-Batch.",
                desc_name,
                sk.value,
            )
            return

        v = validate_feature_registrar(
            reg,
            source_kind=sk,
            known_dependency_group_names=known_dependency_group_names,
            accepted_feature_names=frozenset(names_ok),
            host_version=host_version,
        )
        for w in v.warnings:
            _log.warning("Feature-Governance %r (%s): %s", desc_name, sk.value, w)
        if not v.ok:
            _log.warning(
                "Feature-Governance: Registrar %r übersprungen (%s): %s",
                desc_name,
                sk.value,
                "; ".join(v.errors),
            )
            return
        ic = resolve_feature_compatibility(reg, source_kind=sk).incompatible_features
        conflict = frozenset(ic) & registered_names
        if conflict:
            _log.warning(
                "Feature-Governance: Registrar %r übersprungen (%s): incompatible_features "
                "kollidiert mit bereits registrierten %s",
                desc_name,
                sk.value,
                sorted(conflict),
            )
            return
        accepted.append((reg, sk))
        registered_names.add(desc_name)
        if sk is not FeatureSourceKind.BUILTIN:
            names_ok.add(desc_name)

    for reg, sk in bucket_builtin:
        _try_one(reg, sk)

    for reg, sk in bucket_rest:
        _try_one(reg, sk)

    return accepted
