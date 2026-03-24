"""SettingsAiModelCatalogSink — Combo aus Contract-State."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QComboBox

from app.gui.domains.settings.settings_ai_model_catalog_sink import SettingsAiModelCatalogSink
from app.ui_contracts.workspaces.settings_ai_model_catalog import (
    AI_MODEL_CATALOG_PLACEHOLDER_LOADING,
    AiModelCatalogEntryDto,
    AiModelCatalogState,
)


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


def _entry(sid: str) -> AiModelCatalogEntryDto:
    return AiModelCatalogEntryDto(
        selection_id=sid,
        display_short=sid,
        display_detail="",
        chat_selectable=True,
        asset_type="",
        storage_root_name="",
        path_hint="",
        usage_summary="",
        quota_summary="",
        usage_quality_note="",
    )


def test_sink_loading_row(qapp) -> None:
    combo = QComboBox()
    sink = SettingsAiModelCatalogSink(combo)
    sink.apply_full_catalog_state(
        AiModelCatalogState(
            phase="loading",
            entries=(),
            default_selection_id="",
            display_mode="combo_placeholder",
            placeholder_line=AI_MODEL_CATALOG_PLACEHOLDER_LOADING,
        ),
    )
    assert combo.count() == 1
    assert AI_MODEL_CATALOG_PLACEHOLDER_LOADING in combo.itemText(0)


def test_sink_entries_apply(qapp) -> None:
    combo = QComboBox()
    sink = SettingsAiModelCatalogSink(combo)
    sink.apply_full_catalog_state(
        AiModelCatalogState(
            phase="ready",
            entries=(_entry("a"), _entry("b")),
            default_selection_id="b",
            display_mode="combo_entries",
            placeholder_line="",
        ),
    )
    assert combo.count() >= 2
