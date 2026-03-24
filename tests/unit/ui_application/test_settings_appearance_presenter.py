"""SettingsAppearancePresenter — Qt-frei mit Fake-Port und Recording-Sink."""

from __future__ import annotations

from app.ui_application.presenters.settings_appearance_presenter import SettingsAppearancePresenter
from app.ui_contracts.workspaces.settings_appearance import (
    AppearanceSettingsState,
    AppearanceStatePatch,
    LoadAppearanceSettingsCommand,
    SelectThemeCommand,
    SettingsAppearancePortError,
    ThemeListEntry,
)


class _RecordingSink:
    def __init__(self) -> None:
        self.full_states: list[AppearanceSettingsState] = []
        self.patches: list[AppearanceStatePatch] = []
        self.visual: list[str] = []
        self.visual_succeed = True

    def apply_full_state(self, state: AppearanceSettingsState) -> None:
        self.full_states.append(state)

    def apply_patch(self, patch: AppearanceStatePatch) -> None:
        self.patches.append(patch)

    def apply_selected_theme_visual(self, theme_id: str) -> bool:
        self.visual.append(theme_id)
        return self.visual_succeed


class _FakePort:
    def __init__(self) -> None:
        self.persisted: list[str] = []
        self._state = AppearanceSettingsState(
            themes=(
                ThemeListEntry("light_default", "Light"),
                ThemeListEntry("dark_default", "Dark"),
            ),
            selected_theme_id="light_default",
            error=None,
        )
        self.fail_persist = False

    def load_appearance_state(self) -> AppearanceSettingsState:
        return self._state

    def validate_theme_id(self, theme_id: str) -> bool:
        return theme_id in ("light_default", "dark_default")

    def persist_theme_choice(self, theme_id: str) -> None:
        if self.fail_persist:
            raise SettingsAppearancePortError("persist_failed", "save failed", recoverable=True)
        self.persisted.append(theme_id)
        self._state = AppearanceSettingsState(
            themes=self._state.themes,
            selected_theme_id=theme_id,
            error=None,
        )


def test_load_pushes_full_state() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAppearancePresenter(sink, port)
    p.handle_command(LoadAppearanceSettingsCommand())
    assert len(sink.full_states) == 1
    assert sink.full_states[0].selected_theme_id == "light_default"


def test_select_valid_persists_and_patches() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    committed: list[str] = []
    p = SettingsAppearancePresenter(sink, port, on_theme_choice_committed=committed.append)
    p.handle_command(LoadAppearanceSettingsCommand())
    p.handle_command(SelectThemeCommand("dark_default"))
    assert port.persisted == ["dark_default"]
    assert "dark_default" in sink.visual
    assert committed == ["dark_default"]
    assert sink.patches[-1].selected_theme_id == "dark_default"
    assert sink.patches[-1].has_error_update is True


def test_select_unknown_theme_sets_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAppearancePresenter(sink, port)
    p.handle_command(LoadAppearanceSettingsCommand())
    sink.patches.clear()
    p.handle_command(SelectThemeCommand("nope"))
    assert port.persisted == []
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "unknown_theme"
        for patch in sink.patches
    )


def test_persist_failure_reverts_visual_and_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    port.fail_persist = True
    p = SettingsAppearancePresenter(sink, port)
    p.handle_command(LoadAppearanceSettingsCommand())
    sink.visual.clear()
    p.handle_command(SelectThemeCommand("dark_default"))
    assert sink.visual == ["dark_default", "light_default"]
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "persist_failed"
        for patch in sink.patches
    )


def test_visual_failure_sets_error() -> None:
    sink = _RecordingSink()
    sink.visual_succeed = False
    port = _FakePort()
    p = SettingsAppearancePresenter(sink, port)
    p.handle_command(LoadAppearanceSettingsCommand())
    p.handle_command(SelectThemeCommand("dark_default"))
    assert port.persisted == []
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "theme_apply_failed"
        for patch in sink.patches
    )


def test_no_port_backend_not_wired() -> None:
    sink = _RecordingSink()
    p = SettingsAppearancePresenter(sink, None)
    p.handle_command(LoadAppearanceSettingsCommand())
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "backend_not_wired"
        for patch in sink.patches
    )
