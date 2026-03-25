"""
FeatureRegistrar-Discovery: Builtins, optionale Pakete, Entry Points, Umgebungsmodule.

Kein Plugin-Lifecycle, keine Sandbox — nur Erweiterung der Registrarmenge.

Discovery liefert pro Eintrag eine Quelle (:class:`FeatureSourceKind`); die Registrierung
wende Governance/Validierung an (fail-soft).
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import pkgutil
import types
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Iterator, List, Union

from app.features.compatibility import FeatureSourceKind
from app.features.entry_point_contract import ENTRY_POINT_GROUP
from app.features.feature_validation import plan_registration_order
from app.features.registrar import FeatureRegistrar

if TYPE_CHECKING:
    from app.features.registry import FeatureRegistry

_LOG = logging.getLogger(__name__)

_ENV_EXTRA_MODULES = "LDC_FEATURE_REGISTRAR_MODULES"


@dataclass(frozen=True, slots=True)
class DiscoveredFeatureRegistrar:
    """Ein geladener Registrar plus tatsächliche Discovery-Quelle (für Governance)."""

    registrar: FeatureRegistrar
    source_kind: FeatureSourceKind


def _normalize_registrars(raw: Any) -> List[Any]:
    """Flacht Rückgaben zu einer Liste ab (kein String-Splitting; Einzelobjekte bleiben erhalten)."""
    if raw is None:
        return []
    if isinstance(raw, (str, bytes)):
        return []
    if isinstance(raw, FeatureRegistrar):
        return [raw]
    if isinstance(raw, (list, tuple)):
        return list(raw)
    try:
        return list(raw)
    except TypeError:
        return [raw]


def _is_feature_registrar_like(obj: Any) -> bool:
    """Mindestprüfung vor Yield (Entry Points / Module — Governance folgt später)."""
    if obj is None or isinstance(obj, (str, bytes, int, float, bool, dict, set)):
        return False
    return callable(getattr(obj, "get_descriptor", None)) and callable(getattr(obj, "is_available", None))


def _extract_from_module(mod: Any, source: str) -> List[FeatureRegistrar]:
    out: List[FeatureRegistrar] = []
    if hasattr(mod, "get_feature_registrars"):
        try:
            fn = mod.get_feature_registrars
            raw = fn() if callable(fn) else fn
            out.extend(_normalize_registrars(raw))
        except Exception as exc:  # noqa: BLE001
            _LOG.warning(
                "Feature-Discovery %s: get_feature_registrars() fehlgeschlagen: %s",
                source,
                exc,
            )
    if hasattr(mod, "FEATURE_REGISTRARS"):
        try:
            out.extend(_normalize_registrars(mod.FEATURE_REGISTRARS))
        except Exception as exc:  # noqa: BLE001
            _LOG.warning(
                "Feature-Discovery %s: FEATURE_REGISTRARS unlesbar: %s",
                source,
                exc,
            )
    return out


def _package_has_path(package_name: str) -> bool:
    spec = importlib.util.find_spec(package_name)
    return spec is not None and spec.submodule_search_locations is not None


def _iter_subpackage_feature_registrars(package_name: str) -> Iterator[FeatureRegistrar]:
    if not _package_has_path(package_name):
        return
    try:
        base = importlib.import_module(package_name)
    except Exception as exc:  # noqa: BLE001
        _LOG.warning("Feature-Discovery: Paket %r nicht ladbar: %s", package_name, exc)
        return
    path = getattr(base, "__path__", None)
    if not path:
        return
    for _finder, modname, _ispkg in pkgutil.iter_modules(path, prefix=f"{package_name}."):
        sub = f"{modname}.feature_registrar"
        try:
            mod = importlib.import_module(sub)
        except ImportError:
            continue
        except Exception as exc:  # noqa: BLE001
            _LOG.warning("Feature-Discovery: Modul %r Import fehlgeschlagen: %s", sub, exc)
            continue
        for r in _extract_from_module(mod, sub):
            if _is_feature_registrar_like(r):
                yield r
            else:
                _LOG.warning(
                    "Feature-Discovery %s: Eintrag übersprungen (kein FeatureRegistrar): %r",
                    sub,
                    r,
                )


def _registrars_resolved_from_entry_point_target(loaded: Any, ep_name: str, ep_value: str) -> List[Any]:
    """
    Wert aus ``EntryPoint.load()`` in eine Registrar-Liste überführen.

    Primär: Callable ohne Argumente (typ. ``get_feature_registrars``).
    Modul: wie ``_extract_from_module`` (Callable + ``FEATURE_REGISTRARS``).
    Sonst: Sequenz oder Einzelobjekt (Legacy).
    """
    if isinstance(loaded, types.ModuleType):
        return _extract_from_module(loaded, f"entry_point:{ep_name}")
    if callable(loaded):
        try:
            raw = loaded()
        except TypeError:
            # Z. B. Callable mit Pflichtargumenten — kein stiller Erfolg
            raise
        return _normalize_registrars(raw)
    return _normalize_registrars(loaded)


def _iter_entry_point_registrars() -> Iterator[FeatureRegistrar]:
    try:
        import importlib.metadata as imd
    except ImportError:
        return
    try:
        eps = imd.entry_points()
    except Exception as exc:  # noqa: BLE001
        _LOG.warning("Feature-Discovery: entry_points() fehlgeschlagen: %s", exc)
        return
    if hasattr(eps, "select"):
        selected = list(eps.select(group=ENTRY_POINT_GROUP))
    else:
        selected = list(eps.get(ENTRY_POINT_GROUP, []))
    for ep in selected:
        try:
            loaded: Union[Callable[..., Any], Any] = ep.load()
            batch = _registrars_resolved_from_entry_point_target(loaded, ep.name, ep.value)
        except Exception as exc:  # noqa: BLE001
            _LOG.warning(
                "Feature-Discovery: Entry-Point %r (%s) fehlgeschlagen: %s",
                ep.name,
                ep.value,
                exc,
            )
            continue
        for r in batch:
            if _is_feature_registrar_like(r):
                yield r
            else:
                _LOG.warning(
                    "Feature-Discovery: Entry-Point %r (%s): übersprungen (kein FeatureRegistrar): %r",
                    ep.name,
                    ep.value,
                    r,
                )


def _iter_env_module_registrars() -> Iterator[FeatureRegistrar]:
    raw = os.environ.get(_ENV_EXTRA_MODULES, "")
    if not raw.strip():
        return
    for part in raw.split(","):
        modname = part.strip()
        if not modname:
            continue
        try:
            mod = importlib.import_module(modname)
        except Exception as exc:  # noqa: BLE001
            _LOG.warning("Feature-Discovery: LDC-Modul %r nicht ladbar: %s", modname, exc)
            continue
        for r in _extract_from_module(mod, modname):
            if _is_feature_registrar_like(r):
                yield r
            else:
                _LOG.warning(
                    "Feature-Discovery: LDC-Modul %r: übersprungen (kein FeatureRegistrar): %r",
                    modname,
                    r,
                )


def discover_feature_registrars() -> tuple[DiscoveredFeatureRegistrar, ...]:
    """
    Alle FeatureRegistrare in fester Reihenfolge, jeweils mit :class:`FeatureSourceKind`:

    1. Builtins (app.gui.registration.feature_builtins)
    2. ``app.plugins.<subpkg>.feature_registrar`` (falls Paket existiert)
    3. ``app.extensions.<subpkg>.feature_registrar`` (falls Paket existiert)
    4. Entry-Points ``linux_desktop_chat.features``
    5. Module aus ``LDC_FEATURE_REGISTRAR_MODULES`` (kommasepariert)
    """
    out: List[DiscoveredFeatureRegistrar] = []

    try:
        fb = importlib.import_module("app.gui.registration.feature_builtins")
        for r in fb.iter_builtin_feature_registrars():
            out.append(DiscoveredFeatureRegistrar(r, FeatureSourceKind.BUILTIN))
    except Exception as exc:  # noqa: BLE001
        _LOG.exception("Feature-Discovery: Builtins konnten nicht geladen werden: %s", exc)
        raise

    for r in _iter_subpackage_feature_registrars("app.plugins"):
        out.append(DiscoveredFeatureRegistrar(r, FeatureSourceKind.PLUGIN))
    for r in _iter_subpackage_feature_registrars("app.extensions"):
        out.append(DiscoveredFeatureRegistrar(r, FeatureSourceKind.EXTENSION))
    for r in _iter_entry_point_registrars():
        out.append(DiscoveredFeatureRegistrar(r, FeatureSourceKind.ENTRY_POINT))
    for r in _iter_env_module_registrars():
        out.append(DiscoveredFeatureRegistrar(r, FeatureSourceKind.ENV))

    return tuple(out)


def register_discovered_feature_registrars(registry: "FeatureRegistry") -> int:
    """
    Validiert entdeckte Registrare (Governance) und registriert sie fail-soft.

    Ungültige oder kollidierende Einträge: Warnung im Log, kein Abbruch.

    Returns:
        Anzahl erfolgreich registrierter Registrare.
    """
    from app.features.dependency_groups.registry import (
        build_default_dependency_group_registry,
        get_dependency_group_registry,
    )

    dep = get_dependency_group_registry()
    if dep is None:
        dep = build_default_dependency_group_registry()
    group_names = frozenset(dep.list_groups())

    pairs = [(d.registrar, d.source_kind) for d in discover_feature_registrars()]
    planned = plan_registration_order(pairs, known_dependency_group_names=group_names, log=_LOG)

    n = 0
    for reg, _sk in planned:
        try:
            registry.register_registrar(reg)
            n += 1
        except ValueError as exc:
            _LOG.warning("Feature-Discovery: Registrar übersprungen: %s", exc)
    return n
