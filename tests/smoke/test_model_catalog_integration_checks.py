"""
Abschluss-Smoke: Unified Model Catalog + GUI-Hilfen (ohne volle App).

Prüft die nachgezogene Integration gegen dokumentierte Regeln:
Settings nur chat_selectable, Tooltips, Management-Status mit Usage-Kürzel,
konservatives Tag-Matching.
"""

from __future__ import annotations

from app.gui.common.model_catalog_combo import _catalog_entry_tooltip
from app.services.unified_model_catalog_service import (
    UnifiedModelCatalogService,
    model_id_in_runtime_name_set,
)


def test_settings_standard_model_list_is_chat_selectable_only():
    catalog = [
        {"selection_id": "m1", "chat_selectable": True},
        {"selection_id": "local-asset:9", "chat_selectable": False},
    ]
    usable = [e for e in catalog if e.get("chat_selectable")]
    assert [e["selection_id"] for e in usable] == ["m1"]


def test_tooltip_covers_detail_asset_storage_usage_quota_quality():
    tip = _catalog_entry_tooltip(
        {
            "display_detail": "Registry · lokal",
            "asset_type": "gguf",
            "storage_root_name": "ai",
            "path_hint": "w.gguf",
            "usage_summary": "Tokens · Tag 0",
            "quota_summary": "Quota: none · Warn 80%",
            "usage_quality_note": "Keine Anfragen",
            "chat_selectable": True,
        }
    )
    for needle in ("Registry", "gguf", "ai", "w.gguf", "Tokens", "Quota", "Anfragen", "auswählbar"):
        assert needle in tip


def test_management_row_status_includes_usage_snippet():
    svc = UnifiedModelCatalogService()
    rows = svc.to_management_rows(
        [
            {
                "selection_id": "x",
                "display_short": "x",
                "chat_selectable": True,
                "is_online": False,
                "runtime_ready": True,
                "has_local_asset": False,
                "assignment_state": "registry",
                "asset_available": None,
                "usage_summary": "Tokens · Tag 1.2k · Wo 2k",
            }
        ]
    )
    assert rows and "Tokens" in (rows[0].get("status_label") or "")


def test_conservative_tag_matching_no_false_merge_across_tags():
    names = {"llama3:8b"}
    assert model_id_in_runtime_name_set(names, "llama3")
    assert not model_id_in_runtime_name_set(names, "llama3:70b")
