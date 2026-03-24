"""Settings-Appearance-Contracts: Merge, Serialisierung, Stabilität."""

from __future__ import annotations

from dataclasses import asdict

from app.ui_contracts.workspaces.settings_appearance import (
    AppearanceSettingsState,
    AppearanceStatePatch,
    LoadAppearanceSettingsCommand,
    SelectThemeCommand,
    SettingsAppearancePortError,
    SettingsErrorInfo,
    ThemeListEntry,
    merge_appearance_state,
)


def test_merge_updates_selection_only() -> None:
    base = AppearanceSettingsState(
        themes=(ThemeListEntry("a", "A"),),
        selected_theme_id="a",
        error=None,
    )
    patch = AppearanceStatePatch(selected_theme_id="b")
    merged = merge_appearance_state(base, patch)
    assert merged.selected_theme_id == "b"
    assert merged.error is None


def test_merge_error_with_flag() -> None:
    base = AppearanceSettingsState(
        themes=(),
        selected_theme_id="light_default",
        error=None,
    )
    err = SettingsErrorInfo(code="x", message="m")
    merged = merge_appearance_state(
        base,
        AppearanceStatePatch(error=err, has_error_update=True),
    )
    assert merged.error == err


def test_merge_clear_error_via_patch() -> None:
    base = AppearanceSettingsState(
        themes=(),
        selected_theme_id="light_default",
        error=SettingsErrorInfo(code="x", message="m"),
    )
    merged = merge_appearance_state(
        base,
        AppearanceStatePatch(error=None, has_error_update=True),
    )
    assert merged.error is None


def test_asdict_roundtrip_friendly() -> None:
    state = AppearanceSettingsState(
        themes=(ThemeListEntry("light_default", "Light"),),
        selected_theme_id="light_default",
        error=None,
    )
    d = asdict(state)
    assert d["selected_theme_id"] == "light_default"
    assert d["themes"][0]["theme_id"] == "light_default"


def test_commands_frozen() -> None:
    assert SelectThemeCommand("x").theme_id == "x"
    assert isinstance(LoadAppearanceSettingsCommand(), LoadAppearanceSettingsCommand)


def test_port_error_attrs() -> None:
    exc = SettingsAppearancePortError("code", "msg", recoverable=False)
    assert exc.code == "code"
    assert exc.message == "msg"
    assert exc.recoverable is False
