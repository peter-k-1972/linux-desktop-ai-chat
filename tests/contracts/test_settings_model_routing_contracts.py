"""Settings model routing studio — Contract-DTOs."""

from __future__ import annotations

from dataclasses import replace

from app.ui_contracts.workspaces.settings_model_routing import (
    ApplyModelRoutingStudioPatchCommand,
    ModelRoutingStudioState,
    ModelRoutingStudioWritePatch,
)


def test_write_patch_replace() -> None:
    p = ModelRoutingStudioWritePatch(temperature=0.5)
    q = replace(p, max_tokens=100)
    assert q.temperature == 0.5
    assert q.max_tokens == 100


def test_apply_command_carries_patch() -> None:
    c = ApplyModelRoutingStudioPatchCommand(ModelRoutingStudioWritePatch(auto_routing=False))
    assert c.patch.auto_routing is False


def test_state_frozen_fields() -> None:
    s = ModelRoutingStudioState(
        model="m",
        auto_routing=True,
        cloud_escalation=False,
        cloud_via_local=False,
        web_search=False,
        overkill_mode=False,
        default_role="DEFAULT",
        temperature=0.7,
        top_p=0.9,
        max_tokens=4096,
        llm_timeout_seconds=60,
        retry_without_thinking=True,
        chat_streaming_enabled=True,
        error=None,
    )
    assert s.model == "m"
    assert s.top_p == 0.9
    assert s.llm_timeout_seconds == 60
