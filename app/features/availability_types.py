"""
Reine Datenmodelle für technische Verfügbarkeit (keine Import-Probes hier).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AvailabilityResult:
    """Ergebnis einer Verfügbarkeitsprüfung (Dependency-Gruppe oder Feature)."""

    available: bool
    reason_code: str
    """Kurzcode, z. B. ``ok``, ``import_failed``, ``unknown_group``."""
    message: str = ""
    missing_modules: tuple[str, ...] = ()
    """Module/Distributions, deren Import fehlschlug (Diagnose)."""


@dataclass(frozen=True, slots=True)
class FeatureAvailabilityResult:
    """Feature-Check inkl. fehlgeschlagener Gruppe."""

    available: bool
    reason_code: str
    message: str = ""
    failed_group: str | None = None
    group_result: AvailabilityResult | None = None
