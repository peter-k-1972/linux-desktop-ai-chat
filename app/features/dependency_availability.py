"""
Technische Verfügbarkeit von Dependency-Gruppen und Features.

- Kein GUI-Import.
- Zentrale Import-Probes (repräsentativ, klein); später ersetzbar durch pip-extra-/Build-Manifest.
- Editionen bleiben fachlich maßgeblich; diese Schicht begrenzt die ausführbare Teilmenge (fail-soft).
- Gruppennamen sind identisch zu ``DependencyGroupDescriptor.name`` und zu
  :mod:`app.features.dependency_packaging` (Drift-Tests: ``validate_availability_probe_names_align``).
"""

from __future__ import annotations

import importlib
import logging
import os
from typing import Callable, Optional

from app.features.availability_types import AvailabilityResult, FeatureAvailabilityResult
from app.features.descriptors import FeatureDescriptor
from app.features.dependency_groups.models import DependencyGroupDescriptor
from app.features.dependency_groups.registry import (
    DependencyGroupRegistry,
    build_default_dependency_group_registry,
    get_dependency_group_registry,
)

_LOG = logging.getLogger(__name__)

# Registry-Cache, falls Bootstrap keine globale DependencyGroupRegistry setzt
_cached_dep_registry: Optional[DependencyGroupRegistry] = None


def _effective_dependency_registry() -> DependencyGroupRegistry:
    global _cached_dep_registry
    r = get_dependency_group_registry()
    if r is not None:
        return r
    if _cached_dep_registry is None:
        _cached_dep_registry = build_default_dependency_group_registry()
    return _cached_dep_registry


def is_module_importable(module_name: str) -> AvailabilityResult:
    """
    Prüft, ob ``module_name`` importierbar ist (keine Seiteneffekte außer erfolgreichem Import).

    Bei Fehler: ``reason_code=import_failed``.
    """
    try:
        importlib.import_module(module_name)
        return AvailabilityResult(True, "ok", "")
    except Exception as exc:  # noqa: BLE001 — bewusst breit für Importfehler
        return AvailabilityResult(
            False,
            "import_failed",
            str(exc),
            missing_modules=(module_name,),
        )


# Gruppenname -> Probe (ohne Descriptor, rein technisch)
_GroupProbe = Callable[[], AvailabilityResult]


def _probe_core() -> AvailabilityResult:
    r = is_module_importable("PySide6.QtCore")
    if not r.available:
        return r
    return is_module_importable("aiohttp")


def _probe_rag() -> AvailabilityResult:
    return is_module_importable("chromadb")


def _probe_agents() -> AvailabilityResult:
    return is_module_importable("app.agents")


def _probe_workflows() -> AvailabilityResult:
    return is_module_importable("app.workflows")


def _probe_qml() -> AvailabilityResult:
    return is_module_importable("PySide6.QtQml")


def _probe_dev() -> AvailabilityResult:
    return is_module_importable("pytest")


def _probe_governance() -> AvailabilityResult:
    return is_module_importable("app.services.qa_governance_service")


def _probe_ops() -> AvailabilityResult:
    """Informative Gruppe ohne klaren Single-Module-Test — Monolith enthält Operations-UI."""
    return AvailabilityResult(True, "ok", "ops: keine strikte Modulprobe (Monolith)")


_GROUP_PROBES: dict[str, _GroupProbe] = {
    "core": _probe_core,
    "rag": _probe_rag,
    "agents": _probe_agents,
    "workflows": _probe_workflows,
    "ops": _probe_ops,
    "qml": _probe_qml,
    "dev": _probe_dev,
    "governance": _probe_governance,
}


def check_dependency_group_availability(
    group_name: str,
    *,
    dep_registry: Optional[DependencyGroupRegistry] = None,
) -> AvailabilityResult:
    """
    Technische Verfügbarkeit einer registrierten Dependency-Gruppe.

    Unbekannte Gruppe: ``available=False``, ``reason_code=unknown_group``.
    """
    reg = dep_registry if dep_registry is not None else _effective_dependency_registry()
    desc = reg.get_group(group_name)
    if desc is None:
        return AvailabilityResult(
            False,
            "unknown_group",
            f"Unbekannte Dependency-Gruppe: {group_name!r}",
        )
    probe = _GROUP_PROBES.get(group_name)
    if probe is None:
        return AvailabilityResult(
            True,
            "no_probe",
            f"Gruppe {group_name!r}: keine Modulprobe registriert — als verfügbar angenommen",
        )
    result = probe()
    if not result.available:
        _LOG.debug(
            "dependency group %r unavailable: %s — %s",
            group_name,
            result.reason_code,
            result.message,
        )
    return result


def check_feature_availability(
    descriptor: FeatureDescriptor,
    *,
    dep_registry: Optional[DependencyGroupRegistry] = None,
    require_core: bool = True,
) -> FeatureAvailabilityResult:
    """
    Technische Verfügbarkeit eines Features.

    1. Optional ``core``-Gruppe (GUI/Async-Basis).
    2. Jeder Eintrag in ``descriptor.optional_dependencies`` (Gruppenname) muss verfügbar sein.

    ``optional_dependencies`` sind hier **harte technische Voraussetzungen**, keine Marketing-Extras.
    """
    reg = dep_registry if dep_registry is not None else _effective_dependency_registry()
    if require_core:
        core_r = check_dependency_group_availability("core", dep_registry=reg)
        if not core_r.available:
            return FeatureAvailabilityResult(
                False,
                "core_unavailable",
                core_r.message,
                failed_group="core",
                group_result=core_r,
            )
    for group_name in descriptor.optional_dependencies:
        g_desc = reg.get_group(group_name)
        if g_desc is None:
            return FeatureAvailabilityResult(
                False,
                "unknown_dependency_tag",
                f"Feature {descriptor.name!r}: unbekannte Gruppe {group_name!r}",
                failed_group=group_name,
                group_result=AvailabilityResult(
                    False,
                    "unknown_group",
                    f"Kein DependencyGroupDescriptor für {group_name!r}",
                ),
            )
        gr = check_dependency_group_availability(group_name, dep_registry=reg)
        if not gr.available:
            return FeatureAvailabilityResult(
                False,
                "dependency_group_unavailable",
                f"Feature {descriptor.name!r}: Gruppe {group_name!r} nicht verfügbar — {gr.message}",
                failed_group=group_name,
                group_result=gr,
            )
    return FeatureAvailabilityResult(True, "ok", "")


def is_feature_technically_available(
    descriptor: FeatureDescriptor,
    *,
    dep_registry: Optional[DependencyGroupRegistry] = None,
) -> bool:
    """Kurzform für Registrare: nur bool."""
    if os.environ.get("LDC_IGNORE_TECHNICAL_AVAILABILITY") == "1":
        return True
    return check_feature_availability(descriptor, dep_registry=dep_registry).available


def register_group_probe(group_name: str, probe: _GroupProbe) -> None:
    """Tests: Probe überschreiben oder Gruppe nachregistrieren."""
    _GROUP_PROBES[group_name] = probe
