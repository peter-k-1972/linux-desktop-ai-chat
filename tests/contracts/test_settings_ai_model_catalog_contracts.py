"""Settings — AI Model Catalog (Slice 4b) Contracts."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from dataclasses import asdict

from app.ui_contracts.workspaces.settings_ai_model_catalog import (
    AI_MODEL_CATALOG_PLACEHOLDER_EMPTY_USABLE,
    AiModelCatalogEntryDto,
    AiModelCatalogPortLoadOutcome,
    AiModelCatalogState,
    LoadAiModelCatalogCommand,
    PersistAiModelSelectionCommand,
    RetryAiModelCatalogCommand,
)


def test_catalog_entry_dto_asdict_roundtrip() -> None:
    e = AiModelCatalogEntryDto(
        selection_id="m1",
        display_short="M1",
        display_detail="d",
        chat_selectable=True,
        asset_type="gguf",
        storage_root_name="r",
        path_hint="p",
        usage_summary="u",
        quota_summary="q",
        usage_quality_note="n",
    )
    d = asdict(e)
    assert d["selection_id"] == "m1"
    assert d["chat_selectable"] is True


def test_load_outcome_success_entries() -> None:
    e = AiModelCatalogEntryDto(
        selection_id="x",
        display_short="X",
        display_detail="",
        chat_selectable=True,
        asset_type="",
        storage_root_name="",
        path_hint="",
        usage_summary="",
        quota_summary="",
        usage_quality_note="",
    )
    o = AiModelCatalogPortLoadOutcome(
        status="success_entries",
        entries=(e,),
        default_selection_id="x",
        placeholder_line="",
    )
    assert o.status == "success_entries"
    assert len(o.entries) == 1


def test_catalog_state_placeholder() -> None:
    st = AiModelCatalogState(
        phase="ready",
        entries=(),
        default_selection_id="",
        display_mode="combo_placeholder",
        placeholder_line=AI_MODEL_CATALOG_PLACEHOLDER_EMPTY_USABLE,
    )
    assert st.display_mode == "combo_placeholder"


def test_commands_frozen() -> None:
    assert PersistAiModelSelectionCommand("mid").model_id == "mid"
    assert LoadAiModelCatalogCommand() is not None
    assert RetryAiModelCatalogCommand() is not None
