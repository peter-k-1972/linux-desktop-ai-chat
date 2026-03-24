"""
SettingsAiModelCatalogSink — Modell-Combo aus :class:`AiModelCatalogState` (Slice 4b).
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox

from app.gui.common.model_catalog_combo import apply_catalog_to_combo
from app.ui_contracts.workspaces.settings_ai_model_catalog import (
    AiModelCatalogEntryDto,
    AiModelCatalogState,
)


def _entry_dto_to_combo_dict(e: AiModelCatalogEntryDto) -> dict[str, Any]:
    return {
        "selection_id": e.selection_id,
        "display_short": e.display_short,
        "display_detail": e.display_detail,
        "chat_selectable": e.chat_selectable,
        "asset_type": e.asset_type,
        "storage_root_name": e.storage_root_name,
        "path_hint": e.path_hint,
        "usage_summary": e.usage_summary,
        "quota_summary": e.quota_summary,
        "usage_quality_note": e.usage_quality_note,
    }


class SettingsAiModelCatalogSink:
    def __init__(self, model_combo: QComboBox) -> None:
        self._combo = model_combo

    def _sync_model_from_settings_id(self, current: str) -> None:
        """Wie Legacy ``_sync_model_from_settings``: UserRole zuerst, sonst sichtbarer Text."""
        if not current:
            return
        for i in range(self._combo.count()):
            if self._combo.itemData(i, Qt.ItemDataRole.UserRole) == current:
                self._combo.setCurrentIndex(i)
                return
            if self._combo.itemText(i) == current:
                self._combo.setCurrentIndex(i)
                return

    def sync_to_stored_model(self, model_id: str) -> None:
        """Nach Katalog-Apply: aktuelle Auswahl an gespeicherte Modell-ID angleichen."""
        self._sync_model_from_settings_id(model_id)

    def apply_full_catalog_state(self, state: AiModelCatalogState) -> None:
        self._combo.blockSignals(True)
        try:
            if state.phase == "loading":
                self._combo.clear()
                self._combo.addItem(state.placeholder_line, "")
                return
            if state.display_mode == "combo_placeholder":
                self._combo.clear()
                self._combo.addItem(state.placeholder_line, "")
                return
            rows = [_entry_dto_to_combo_dict(e) for e in state.entries]
            apply_catalog_to_combo(
                self._combo,
                rows,
                default_selection_id=state.default_selection_id or None,
            )
            self._sync_model_from_settings_id(state.default_selection_id)
        finally:
            self._combo.blockSignals(False)
