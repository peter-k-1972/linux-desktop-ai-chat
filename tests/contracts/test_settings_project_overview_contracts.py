"""Contracts: Settings-Projektübersicht."""

from __future__ import annotations

from dataclasses import asdict

from app.ui_contracts.workspaces.settings_project_overview import (
    ActiveProjectSummaryDto,
    RefreshSettingsActiveProjectCommand,
    SettingsActiveProjectViewState,
    SettingsProjectCategoryBodyState,
)


def test_summary_dto_asdict() -> None:
    d = ActiveProjectSummaryDto(
        project_id=1,
        name="P",
        status="active",
        description_display="—",
        chat_count=3,
        default_context_policy_display="—",
        updated_at_display="today",
    )
    assert asdict(d)["project_id"] == 1


def test_view_state_error() -> None:
    st = SettingsActiveProjectViewState(mode="error", error_message="x")
    assert st.error_message == "x"


def test_body_state() -> None:
    assert SettingsProjectCategoryBodyState(body_text="a").body_text == "a"


def test_command() -> None:
    assert isinstance(RefreshSettingsActiveProjectCommand(), RefreshSettingsActiveProjectCommand)
