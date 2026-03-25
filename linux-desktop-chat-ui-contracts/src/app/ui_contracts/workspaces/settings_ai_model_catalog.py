"""
Settings — AI Models: Unified Model Catalog (async slice, Qt-frei).

Slice 4b: Katalog-Laden, Lade-/Fehler-/Leerzustände, Persistenz des Standardmodells.
Skalare AI-Parameter bleiben in ``settings_ai_models``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union

CatalogLoadStatus = Literal[
    "success_entries",
    "success_empty_usable",
    "failure_operational_error",
    "failure_schema_missing",
    "failure_generic",
]

CatalogUiPhase = Literal["idle", "loading", "ready"]

CatalogDisplayMode = Literal["combo_entries", "combo_placeholder"]

# Platzhaltertexte — 1:1 zum Legacy-Panel (vor Slice 4b), damit UX gleich bleibt.
AI_MODEL_CATALOG_PLACEHOLDER_EMPTY_USABLE = (
    "(Keine nutzbaren Modelle – Ollama/Cloud prüfen)"
)
AI_MODEL_CATALOG_PLACEHOLDER_OPERATIONAL_ERROR = (
    "(Datenbank-Schema fehlt – Alembic-Migration ausführen)"
)
AI_MODEL_CATALOG_PLACEHOLDER_GENERIC = "(Keine Modelle – Ollama starten?)"
AI_MODEL_CATALOG_PLACEHOLDER_SCHEMA_HEURISTIC = (
    "(Datenbank-Schema fehlt – Migration ausführen)"
)
AI_MODEL_CATALOG_PLACEHOLDER_LOADING = "(Modellliste wird geladen…)"


@dataclass(frozen=True, slots=True)
class AiModelCatalogEntryDto:
    """Ein Eintrag für die Modell-Combo (Felder wie ``model_catalog_combo.apply_catalog_to_combo``)."""

    selection_id: str
    display_short: str
    display_detail: str
    chat_selectable: bool
    asset_type: str
    storage_root_name: str
    path_hint: str
    usage_summary: str
    quota_summary: str
    usage_quality_note: str


@dataclass(frozen=True, slots=True)
class AiModelCatalogPortLoadOutcome:
    """Ergebnis eines async Katalog-Ladevorgangs (Port → Presenter)."""

    status: CatalogLoadStatus
    entries: tuple[AiModelCatalogEntryDto, ...]
    default_selection_id: str
    placeholder_line: str


@dataclass(frozen=True, slots=True)
class AiModelCatalogState:
    """GUI-neutraler Katalog-Zustand für die Combo."""

    phase: CatalogUiPhase
    entries: tuple[AiModelCatalogEntryDto, ...]
    default_selection_id: str
    display_mode: CatalogDisplayMode
    placeholder_line: str


@dataclass(frozen=True, slots=True)
class LoadAiModelCatalogCommand:
    """Erstes oder erneutes Laden (ohne Retry-Semantik im Namen nötig)."""


@dataclass(frozen=True, slots=True)
class RetryAiModelCatalogCommand:
    """Expliziter Retry (z. B. nach DB-/Schema-Fix)."""


@dataclass(frozen=True, slots=True)
class PersistAiModelSelectionCommand:
    """Nutzer hat ein auswählbares Modell gewählt (selection_id)."""

    model_id: str


AiModelCatalogCommand = Union[
    LoadAiModelCatalogCommand,
    RetryAiModelCatalogCommand,
    PersistAiModelSelectionCommand,
]
