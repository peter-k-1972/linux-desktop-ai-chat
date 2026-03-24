"""SettingsProjectOverviewPresenter — Fake-Port + Recording-Sink."""

from __future__ import annotations

from app.ui_application.presenters.settings_project_overview_presenter import (
    SettingsProjectOverviewPresenter,
)
from app.ui_contracts.workspaces.settings_project_overview import (
    ActiveProjectSummaryDto,
    RefreshSettingsActiveProjectCommand,
    SettingsActiveProjectViewState,
    SettingsProjectCategoryBodyState,
)


class _RecSink:
    def __init__(self) -> None:
        self.bodies: list[SettingsProjectCategoryBodyState] = []

    def apply_body_state(self, state: SettingsProjectCategoryBodyState) -> None:
        self.bodies.append(state)


class _FakePort:
    def __init__(self, state: SettingsActiveProjectViewState) -> None:
        self._state = state

    def load_active_project_view_state(self) -> SettingsActiveProjectViewState:
        return self._state


def test_no_active() -> None:
    sink = _RecSink()
    p = SettingsProjectOverviewPresenter(sink, _FakePort(SettingsActiveProjectViewState(mode="no_active")))
    p.handle_command(RefreshSettingsActiveProjectCommand())
    assert "kein Projekt aktiv" in sink.bodies[0].body_text


def test_ok_summary() -> None:
    sink = _RecSink()
    summary = ActiveProjectSummaryDto(
        project_id=7,
        name="Alpha",
        status="open",
        description_display="Desc",
        chat_count=2,
        default_context_policy_display="pol",
        updated_at_display="2020",
    )
    p = SettingsProjectOverviewPresenter(
        sink, _FakePort(SettingsActiveProjectViewState(mode="ok", summary=summary))
    )
    p.handle_command(RefreshSettingsActiveProjectCommand())
    assert "Alpha (ID 7)" in sink.bodies[0].body_text
    assert "Zugeordnete Chats: 2" in sink.bodies[0].body_text
