"""
Adapter: Unified Model Catalog + Standardmodell-Persistenz für Settings (Slice 4b).

Technische Schuld:
- Katalog kommt weiter aus ``app.services.unified_model_catalog_service`` (async, DB-anfällig).
- ``persist_default_chat_model_id`` schluckt Fehler wie das Legacy-Panel — bewusst kein neues UX-Verhalten.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.infrastructure import get_infrastructure

try:
    from sqlalchemy.exc import OperationalError as _SqlalchemyOperationalError
except ImportError:

    class _SqlalchemyOperationalError(Exception):  # pragma: no cover - nur ohne sqlalchemy
        """Platzhalter, damit der Adapter importierbar bleibt."""
from app.ui_contracts.workspaces.settings_ai_model_catalog import (
    AI_MODEL_CATALOG_PLACEHOLDER_EMPTY_USABLE,
    AI_MODEL_CATALOG_PLACEHOLDER_GENERIC,
    AI_MODEL_CATALOG_PLACEHOLDER_OPERATIONAL_ERROR,
    AI_MODEL_CATALOG_PLACEHOLDER_SCHEMA_HEURISTIC,
    AiModelCatalogEntryDto,
    AiModelCatalogPortLoadOutcome,
)

logger = logging.getLogger(__name__)


def _catalog_dict_to_dto(e: dict[str, Any]) -> AiModelCatalogEntryDto:
    sid = str(e.get("selection_id") or "")
    disp = (e.get("display_short") or e.get("selection_id") or "?").strip() or "?"
    return AiModelCatalogEntryDto(
        selection_id=sid,
        display_short=disp,
        display_detail=str(e.get("display_detail") or ""),
        chat_selectable=bool(e.get("chat_selectable")),
        asset_type=str(e.get("asset_type") or ""),
        storage_root_name=str(e.get("storage_root_name") or ""),
        path_hint=str(e.get("path_hint") or ""),
        usage_summary=str(e.get("usage_summary") or ""),
        quota_summary=str(e.get("quota_summary") or ""),
        usage_quality_note=str(e.get("usage_quality_note") or ""),
    )


class ServiceAiModelCatalogAdapter:
    """Delegiert an ``get_unified_model_catalog_service().build_catalog_for_chat``."""

    async def load_chat_selectable_catalog_for_settings(self) -> AiModelCatalogPortLoadOutcome:
        from app.services.unified_model_catalog_service import get_unified_model_catalog_service

        settings = get_infrastructure().settings
        default_selection_id = str(getattr(settings, "model", "") or "")
        try:
            catalog = await get_unified_model_catalog_service().build_catalog_for_chat(settings)
            usable_raw = [e for e in catalog if e.get("chat_selectable")]
            entries = tuple(_catalog_dict_to_dto(e) for e in usable_raw)
            if not entries:
                return AiModelCatalogPortLoadOutcome(
                    status="success_empty_usable",
                    entries=(),
                    default_selection_id=default_selection_id,
                    placeholder_line=AI_MODEL_CATALOG_PLACEHOLDER_EMPTY_USABLE,
                )
            return AiModelCatalogPortLoadOutcome(
                status="success_entries",
                entries=entries,
                default_selection_id=default_selection_id,
                placeholder_line="",
            )
        except _SqlalchemyOperationalError as exc:
            logger.warning("Modellkatalog: DB/Schema (Migration?): %s", exc)
            return AiModelCatalogPortLoadOutcome(
                status="failure_operational_error",
                entries=(),
                default_selection_id=default_selection_id,
                placeholder_line=AI_MODEL_CATALOG_PLACEHOLDER_OPERATIONAL_ERROR,
            )
        except Exception as exc:
            logger.warning("Modellkatalog laden fehlgeschlagen: %s", exc, exc_info=True)
            msg_lower = str(exc).lower()
            if "no such table" in msg_lower:
                return AiModelCatalogPortLoadOutcome(
                    status="failure_schema_missing",
                    entries=(),
                    default_selection_id=default_selection_id,
                    placeholder_line=AI_MODEL_CATALOG_PLACEHOLDER_SCHEMA_HEURISTIC,
                )
            return AiModelCatalogPortLoadOutcome(
                status="failure_generic",
                entries=(),
                default_selection_id=default_selection_id,
                placeholder_line=AI_MODEL_CATALOG_PLACEHOLDER_GENERIC,
            )

    def persist_default_chat_model_id(self, model_id: str) -> None:
        mid = (model_id or "").strip()
        if not mid:
            return
        try:
            settings = get_infrastructure().settings
            settings.model = mid
            settings.save()
        except Exception as exc:
            logger.warning("Standardmodell konnte nicht gespeichert werden: %s", exc, exc_info=True)
