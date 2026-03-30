"""Settings-AI-Models (skalar) — Contracts."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from dataclasses import asdict

from app.ui_contracts.workspaces.settings_ai_models import (
    AiModelsScalarSettingsPatch,
    AiModelsScalarSettingsState,
    AiModelsScalarWritePatch,
    LoadAiModelsScalarSettingsCommand,
    MAX_TOKENS_MAX,
    SetAiModelsTemperatureCommand,
    THINK_MODES,
    SettingsAiModelsPortError,
    merge_ai_models_scalar_state,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


def test_merge_error_flag() -> None:
    base = AiModelsScalarSettingsState(
        temperature=0.5,
        max_tokens=2048,
        think_mode="low",
        chat_streaming_enabled=False,
        error=None,
    )
    err = SettingsErrorInfo(code="x", message="m")
    m = merge_ai_models_scalar_state(
        base,
        AiModelsScalarSettingsPatch(error=err, has_error_update=True),
    )
    assert m.error == err
    assert m.temperature == 0.5


def test_merge_scalar_fields() -> None:
    base = AiModelsScalarSettingsState(
        temperature=0.7,
        max_tokens=4096,
        think_mode="auto",
        chat_streaming_enabled=True,
        error=None,
    )
    m = merge_ai_models_scalar_state(
        base,
        AiModelsScalarSettingsPatch(temperature=1.2, max_tokens=8192),
    )
    assert m.temperature == 1.2
    assert m.max_tokens == 8192
    assert m.think_mode == "auto"


def test_write_patch_asdict() -> None:
    w = AiModelsScalarWritePatch(temperature=0.3, think_mode="high")
    d = asdict(w)
    assert d["temperature"] == 0.3
    assert d["think_mode"] == "high"


def test_think_modes_contains_auto() -> None:
    assert "auto" in THINK_MODES


def test_commands_frozen() -> None:
    assert SetAiModelsTemperatureCommand(1.0).value == 1.0
    assert LoadAiModelsScalarSettingsCommand() is not None


def test_port_error_attrs() -> None:
    e = SettingsAiModelsPortError("code", "msg", recoverable=False)
    assert e.code == "code"
    assert e.message == "msg"
    assert e.recoverable is False


def test_max_tokens_bounds_constant() -> None:
    assert MAX_TOKENS_MAX == 32768
