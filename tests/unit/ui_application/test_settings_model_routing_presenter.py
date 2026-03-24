"""SettingsModelRoutingPresenter."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.ui_application.presenters.settings_model_routing_presenter import SettingsModelRoutingPresenter
from app.ui_contracts.workspaces.settings_model_routing import (
    ApplyModelRoutingStudioPatchCommand,
    LoadModelRoutingStudioCommand,
    ModelRoutingStudioState,
    ModelRoutingStudioWritePatch,
)


def test_load_command_applies_sink() -> None:
    sink = MagicMock()
    port = MagicMock()
    port.load_model_routing_studio_state.return_value = ModelRoutingStudioState(
        model="x",
        auto_routing=True,
        cloud_escalation=False,
        cloud_via_local=False,
        web_search=False,
        overkill_mode=False,
        default_role="DEFAULT",
        temperature=0.5,
        top_p=1.0,
        max_tokens=100,
        llm_timeout_seconds=0,
        retry_without_thinking=True,
        chat_streaming_enabled=True,
        error=None,
    )
    pre = SettingsModelRoutingPresenter(sink, port)
    pre.handle_command(LoadModelRoutingStudioCommand())
    sink.apply_full_state.assert_called_once()
    port.load_model_routing_studio_state.assert_called_once()


def test_patch_command_persists_and_reloads() -> None:
    sink = MagicMock()
    port = MagicMock()
    st = ModelRoutingStudioState(
        model="m",
        auto_routing=False,
        cloud_escalation=False,
        cloud_via_local=False,
        web_search=False,
        overkill_mode=False,
        default_role="DEFAULT",
        temperature=0.1,
        top_p=0.95,
        max_tokens=50,
        llm_timeout_seconds=30,
        retry_without_thinking=False,
        chat_streaming_enabled=False,
        error=None,
    )
    port.load_model_routing_studio_state.return_value = st
    pre = SettingsModelRoutingPresenter(sink, port)
    pre.handle_command(
        ApplyModelRoutingStudioPatchCommand(ModelRoutingStudioWritePatch(auto_routing=False)),
    )
    port.persist_model_routing_studio.assert_called_once()
    port.load_model_routing_studio_state.assert_called_once()
    sink.apply_full_state.assert_called_once_with(st)
