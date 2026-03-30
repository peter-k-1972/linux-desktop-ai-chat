"""Contracts: Model-Usage-Sidebar-Hinweis."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from dataclasses import asdict

from app.ui_contracts.workspaces.model_usage_sidebar import (
    ModelUsageSidebarHintState,
    RefreshModelUsageSidebarHintCommand,
)


def test_state_serializable() -> None:
    st = ModelUsageSidebarHintState(hint_text="x")
    assert asdict(st)["hint_text"] == "x"


def test_command_frozen() -> None:
    assert isinstance(RefreshModelUsageSidebarHintCommand(), RefreshModelUsageSidebarHintCommand)
