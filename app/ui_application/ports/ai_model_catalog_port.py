"""
AiModelCatalogPort — async Katalog + synchrone Modell-Persistenz (Qt-frei).

Bewusst getrennt von :class:`SettingsOperationsPort`: Async-Lesezugriff und DB-Risiken
gehören nicht auf dasselbe synchrone Settings-Protocol wie skalare Spinbox-Felder.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol, runtime_checkable

from app.ui_contracts.workspaces.settings_ai_model_catalog import AiModelCatalogPortLoadOutcome


@runtime_checkable
class UiCoroutineScheduler(Protocol):
    """Startet eine Coroutine im GUI-gestützten asyncio-Loop (oder stellt später erneut sicher)."""

    def schedule(self, coroutine_factory: Callable[[], Awaitable[None]]) -> None:
        ...


@runtime_checkable
class AiModelCatalogPort(Protocol):
    """Unified Model Catalog für Settings: nur technische Delegation, keine neue Fachlogik."""

    async def load_chat_selectable_catalog_for_settings(self) -> AiModelCatalogPortLoadOutcome:
        """Baut den Chat-kompatiblen Katalog; OperationalError/Schema wie Legacy behandeln."""
        ...

    def persist_default_chat_model_id(self, model_id: str) -> None:
        """
        Schreibt ``AppSettings.model`` + ``save()`` wie bisheriges Panel.

        Technische Schuld: Fehler werden protokolliert, nicht propagiert — entspricht dem
        Legacy-``except Exception: pass`` im Widget; harte Fehler sollten langfristig sichtbar werden.
        """
        ...
