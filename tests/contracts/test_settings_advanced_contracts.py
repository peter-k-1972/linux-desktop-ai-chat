"""Settings-Advanced-Contracts (Qt-frei)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from dataclasses import asdict

from app.ui_contracts.workspaces.settings_advanced import (
    AdvancedSettingsPatch,
    AdvancedSettingsState,
    AdvancedSettingsWritePatch,
    LoadAdvancedSettingsCommand,
    SetChatContextModeCommand,
    SettingsAdvancedPortError,
    merge_advanced_state,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


def test_merge_preserves_unchanged_fields() -> None:
    base = AdvancedSettingsState(
        debug_panel_enabled=True,
        context_debug_enabled=False,
        chat_context_mode="semantic",
        error=None,
    )
    patch = AdvancedSettingsPatch(debug_panel_enabled=False)
    m = merge_advanced_state(base, patch)
    assert m.debug_panel_enabled is False
    assert m.context_debug_enabled is False
    assert m.chat_context_mode == "semantic"


def test_merge_error_flag() -> None:
    base = AdvancedSettingsState(
        debug_panel_enabled=True,
        context_debug_enabled=False,
        chat_context_mode="off",
        error=None,
    )
    err = SettingsErrorInfo(code="x", message="m")
    m = merge_advanced_state(
        base,
        AdvancedSettingsPatch(error=err, has_error_update=True),
    )
    assert m.error == err


def test_write_patch_asdict() -> None:
    w = AdvancedSettingsWritePatch(debug_panel_enabled=True)
    d = asdict(w)
    assert d["debug_panel_enabled"] is True
    assert d["context_debug_enabled"] is None


def test_commands_frozen() -> None:
    assert SetChatContextModeCommand("neutral").mode == "neutral"
    assert isinstance(LoadAdvancedSettingsCommand(), LoadAdvancedSettingsCommand)


def test_port_error_attrs() -> None:
    exc = SettingsAdvancedPortError("c", "m", recoverable=False)
    assert exc.code == "c"
    assert exc.recoverable is False
