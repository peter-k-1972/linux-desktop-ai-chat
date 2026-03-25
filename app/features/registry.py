"""
FeatureRegistry — hält FeatureRegistrar, Reihenfolge, enabled-Flags.

Keine Imports aus app.gui auf Modul-Ebene (build_default lazy).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from app.features.descriptors import FeatureDescriptor
from app.features.registrar import FeatureRegistrar

_default_registry: Optional["FeatureRegistry"] = None


class _DescriptorOnlyRegistrar:
    """Legacy/Test: nur Metadaten, keine Screen-Registrierung."""

    def __init__(self, descriptor: FeatureDescriptor) -> None:
        self._descriptor = descriptor

    def get_descriptor(self) -> FeatureDescriptor:
        return self._descriptor

    def register_screens(self, screen_registry: Any) -> None:
        return None

    def register_navigation(self, context: Any) -> None:
        return None

    def register_commands(self, context: Any) -> None:
        return None

    def register_services(self, context: Any) -> None:
        return None

    def is_available(self) -> bool:
        return True


@dataclass
class FeatureRegistry:
    """
    Registrierung von FeatureRegistrar in fester Reihenfolge.

    ``enabled`` pro Name: Edition-Maske überschreibt ``enabled_by_default`` nach dem Registrieren.
    """

    _order: list[str] = field(default_factory=list)
    _registrars: dict[str, FeatureRegistrar] = field(default_factory=dict)
    _enabled: dict[str, bool] = field(default_factory=dict)
    edition_name: Optional[str] = None
    """Zuletzt gewählte Edition beim Bootstrap (Diagnose, kein Gating in Domänen)."""

    def register_registrar(self, registrar: FeatureRegistrar, *, enabled: Optional[bool] = None) -> None:
        desc = registrar.get_descriptor()
        if desc.name in self._registrars:
            raise ValueError(f"FeatureRegistrar bereits registriert: {desc.name!r}")
        self._order.append(desc.name)
        self._registrars[desc.name] = registrar
        if enabled is None:
            self._enabled[desc.name] = desc.enabled_by_default
        else:
            self._enabled[desc.name] = enabled

    def get_registrar(self, name: str) -> Optional[FeatureRegistrar]:
        return self._registrars.get(name)

    def list_registrars(self) -> tuple[FeatureRegistrar, ...]:
        return tuple(self._registrars[n] for n in self._order)

    def list_registrar_names(self) -> tuple[str, ...]:
        return tuple(self._order)

    def list_enabled_registrars(self) -> tuple[FeatureRegistrar, ...]:
        out: list[FeatureRegistrar] = []
        for name in self._order:
            if not self._enabled.get(name, True):
                continue
            reg = self._registrars[name]
            if reg.is_available():
                out.append(reg)
        return tuple(out)

    def is_registrar_enabled(self, name: str) -> bool:
        return bool(self._enabled.get(name, True))

    def apply_active_feature_mask(self, active_names: frozenset[str]) -> None:
        """Setzt ``enabled`` exakt nach Edition-Feature-Menge (alle Registrare müssen bereits eingetragen sein)."""
        for name in self._order:
            self._enabled[name] = name in active_names

    # --- Abwärtskompatibilität Phase 1 (Deskriptor-only) ---

    def register_feature(self, descriptor: FeatureDescriptor, *, active: bool = True) -> None:
        self.register_registrar(_DescriptorOnlyRegistrar(descriptor), enabled=active)

    def get_feature(self, name: str) -> Optional[FeatureDescriptor]:
        r = self.get_registrar(name)
        return r.get_descriptor() if r else None

    def list_features(self) -> tuple[str, ...]:
        return tuple(sorted(self._registrars.keys()))

    def list_active_features(self) -> tuple[str, ...]:
        return tuple(
            n
            for n in self._order
            if self._enabled.get(n, True) and self._registrars[n].is_available()
        )

    def is_active(self, name: str) -> bool:
        return name in self.list_active_features()


def apply_feature_screen_registrars(
    feature_registry: FeatureRegistry,
    screen_registry: Any,
    *,
    log_skipped: Optional[Any] = None,
) -> int:
    """
    Ruft ``register_screens`` für alle enabled + available Registrare auf.

    Edition-aktiv aber ``is_available()`` False: Warnung, kein Abbruch.

    Returns:
        Anzahl erfolgreich aufgerufener Registrare (nur die mit Screens).
    """
    import logging

    _log = log_skipped or logging.getLogger(__name__)
    count = 0
    for name in feature_registry.list_registrar_names():
        if not feature_registry.is_registrar_enabled(name):
            continue
        reg = feature_registry.get_registrar(name)
        if reg is None:
            continue
        desc = reg.get_descriptor()
        if not reg.is_available():
            _log.warning(
                "Feature %r: laut Edition aktiv, Registrar unavailable — register_screens übersprungen",
                desc.name,
            )
            continue
        try:
            reg.register_screens(screen_registry)
            count += 1
        except Exception:
            _log.exception("feature register_screens failed: %s", desc.name)
            raise
    return count


def build_default_feature_registry() -> FeatureRegistry:
    """Abwärtskompatibel: Default-Edition (``full``) — alle eingebauten Features aktiv."""
    from app.features.edition_resolution import DEFAULT_DESKTOP_EDITION, build_feature_registry_for_edition

    return build_feature_registry_for_edition(DEFAULT_DESKTOP_EDITION)


def set_feature_registry(registry: Optional[FeatureRegistry]) -> None:
    global _default_registry
    _default_registry = registry


def get_feature_registry() -> Optional[FeatureRegistry]:
    return _default_registry
