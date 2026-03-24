"""
Abstrakte UI-Runtime — verbindet ein Theme-Manifest mit Framework-spezifischer Anwendung.

Keine Service-Aufrufe; keine Fachlogik.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.ui_runtime.manifest_models import ThemeManifest


class BaseRuntime(ABC):
    """Gemeinsame Basis für Widgets- und QML-Runtime."""

    def __init__(self, manifest: ThemeManifest) -> None:
        self._manifest = manifest

    @property
    def manifest(self) -> ThemeManifest:
        return self._manifest

    @abstractmethod
    def activate(self, context: dict[str, Any] | None = None) -> None:
        """Theme an die Laufzeit anbinden (QSS, QML-Importpfade, …)."""
        raise NotImplementedError

    @abstractmethod
    def deactivate(self) -> None:
        """Aufräumen (optional no-op in Phase 1)."""
        raise NotImplementedError
