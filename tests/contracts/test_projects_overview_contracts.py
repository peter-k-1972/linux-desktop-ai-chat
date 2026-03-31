"""Contracts: Projects Slice 1 Overview."""

from __future__ import annotations

from dataclasses import asdict

import pytest

from app.ui_contracts.workspaces.projects_overview import (
    ActiveProjectChangedPayload,
    ActiveProjectSnapshot,
    CommandResult,
    ProjectCoreView,
    ProjectInspectorState,
    ProjectListItem,
    ProjectListLoadResult,
    ProjectOverviewState,
    ProjectSelectionChangedPayload,
    ProjectStatsView,
    SubscriptionHandle,
)

pytestmark = pytest.mark.contract


def test_project_list_item_asdict() -> None:
    item = ProjectListItem(
        project_id=1,
        display_name="P",
        secondary_text="Kunde",
        lifecycle_label="Aktiv",
        status_label="active",
        last_activity_label="01.01.2026 12:00",
        is_active=True,
        is_selected=False,
    )
    assert asdict(item)["project_id"] == 1


def test_project_list_load_result() -> None:
    result = ProjectListLoadResult(items=(), empty_reason="no_projects")
    assert result.empty_reason == "no_projects"


def test_overview_state_basic() -> None:
    core = ProjectCoreView(
        project_id=3,
        name="Projekt",
        description_display="—",
        lifecycle_label="Aktiv",
        status_label="active",
        default_context_policy_label="—",
    )
    stats = ProjectStatsView(workflow_count=1, chat_count=2, agent_count=3, file_count=4)
    state = ProjectOverviewState(
        project_id=3,
        core=core,
        stats=stats,
        monitoring=object(),  # type: ignore[arg-type]
        activity=object(),  # type: ignore[arg-type]
        controlling=object(),  # type: ignore[arg-type]
        can_set_active=True,
        is_active_project=False,
    )
    assert state.project_id == 3


def test_inspector_state() -> None:
    st = ProjectInspectorState(
        project_id=4,
        title="P",
        status_label="active",
        lifecycle_label="Aktiv",
        context_policy_caption="—",
        context_rules_narrative="Regeln",
    )
    assert st.title == "P"


def test_active_project_snapshot_and_payloads() -> None:
    snap = ActiveProjectSnapshot(active_project_id=7, is_any_project_active=True, active_project_name="P")
    sel = ProjectSelectionChangedPayload(selected_project_id=7, selected_project_name="P")
    act = ActiveProjectChangedPayload(active_project_id=7, is_any_project_active=True)
    assert snap.active_project_id == 7
    assert sel.selected_project_name == "P"
    assert act.is_any_project_active is True


def test_command_result() -> None:
    result = CommandResult(ok=False, message="x")
    assert result.ok is False
    assert result.message == "x"


def test_subscription_handle_disposes_only_once() -> None:
    calls: list[str] = []
    handle = SubscriptionHandle(lambda: calls.append("disposed"))
    handle.dispose()
    handle.dispose()
    assert calls == ["disposed"]
