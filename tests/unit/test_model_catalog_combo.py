"""model_catalog_combo: Tooltip aus Katalogfeldern."""

from __future__ import annotations

from app.gui.common.model_catalog_combo import _catalog_entry_tooltip


def test_catalog_tooltip_includes_usage_and_quota():
    e = {
        "display_detail": "Registry · lokal",
        "asset_type": "gguf",
        "storage_root_name": "ai",
        "path_hint": "weights.gguf",
        "usage_summary": "Tokens · Tag 0",
        "quota_summary": "Quota: none",
        "usage_quality_note": "note",
        "chat_selectable": True,
    }
    t = _catalog_entry_tooltip(e)
    assert "Registry" in t
    assert "gguf" in t
    assert "Tokens" in t
    assert "Quota" in t
    assert "auswählbar" in t
