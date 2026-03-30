"""Settings Legacy Modal — Contract-DTO (Qt-frei)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from dataclasses import replace

from app.ui_contracts.workspaces.settings_legacy_modal import (
    SettingsLegacyModalCommit,
    SettingsLegacyModalPortError,
)


def test_legacy_modal_commit_replace() -> None:
    a = SettingsLegacyModalCommit(
        model_id="m1",
        temperature=0.1,
        max_tokens=100,
        legacy_theme="dark",
        think_mode="off",
        auto_routing=False,
        cloud_escalation=True,
        cloud_via_local=True,
        overkill_mode=True,
        rag_enabled=False,
        rag_space="default",
        rag_top_k=3,
        self_improving_enabled=False,
        debug_panel_enabled=True,
        prompt_storage_type="database",
        prompt_directory="",
        prompt_confirm_delete=True,
        ollama_api_key="",
    )
    b = replace(a, model_id="m2", temperature=0.9)
    assert b.model_id == "m2"
    assert b.temperature == 0.9
    assert b.legacy_theme == "dark"


def test_legacy_modal_port_error_attrs() -> None:
    e = SettingsLegacyModalPortError("x", "msg", recoverable=False)
    assert e.code == "x"
    assert e.message == "msg"
    assert e.recoverable is False
