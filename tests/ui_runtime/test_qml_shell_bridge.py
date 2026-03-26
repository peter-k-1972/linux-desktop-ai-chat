from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtCore import QUrl

from app.core.navigation.nav_areas import NavArea
from app.ui_runtime.qml.shell_bridge_facade import ShellBridgeFacade


@pytest.fixture
def qml_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "qml"
    assert root.is_dir()
    return root


def test_shell_initial_route_operations_projects(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    assert bridge.activeTopArea == NavArea.OPERATIONS
    assert bridge.activeWorkspaceId == "operations_projects"
    assert bridge.activeDomain == "projects"
    assert bridge.shellReady is True
    assert bridge.stageUrl.isValid()
    assert "ProjectStage.qml" in bridge.stageUrl.toLocalFile()
    assert bridge.routeDeferReason == ""


def test_shell_invalid_domain_ignored(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    before_area = bridge.activeTopArea
    url_before = bridge.stageUrl
    bridge.requestDomainChange("not_a_domain")
    assert bridge.activeTopArea == before_area
    assert bridge.stageUrl == url_before


def test_shell_navigate_legacy_flat_round_trip(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestDomainChange("settings")
    assert bridge.activeTopArea == NavArea.SETTINGS
    assert bridge.activeWorkspaceId == ""
    assert bridge.activeDomain == "settings"
    assert "domains/settings/SettingsStage.qml" in bridge.stageUrl.toLocalFile()
    bridge.requestDomainChange("chat")
    assert bridge.activeTopArea == NavArea.OPERATIONS
    assert bridge.activeWorkspaceId == "operations_chat"
    assert bridge.activeDomain == "chat"


def test_shell_request_route_change(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestRouteChange(NavArea.OPERATIONS, "operations_workflows")
    assert bridge.activeWorkspaceId == "operations_workflows"
    assert "WorkflowStage.qml" in bridge.stageUrl.toLocalFile()


def test_shell_defer_unbound_workspace(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestOperationsWorkspaceChange("operations_knowledge")
    assert "DeferStage.qml" in bridge.stageUrl.toLocalFile()
    assert bridge.routeDeferReason.startswith("unbound:")


def test_shell_defer_command_center(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestTopAreaChange(NavArea.COMMAND_CENTER)
    assert bridge.activeTopArea == NavArea.COMMAND_CENTER
    assert "DeferStage.qml" in bridge.stageUrl.toLocalFile()
    assert "unbound_area" in bridge.routeDeferReason


def test_shell_pending_context_json(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    payload = json.dumps({"workflow_ops_run_id": "wr_1"}, separators=(",", ":"), sort_keys=True)
    bridge.requestRouteChangeWithContextJson(
        NavArea.OPERATIONS,
        "operations_workflows",
        payload,
    )
    assert bridge.pendingContextJson == payload
    bridge.clearPendingContext()
    assert bridge.pendingContextJson == ""


def test_domain_nav_model_row_count(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    m = bridge.domainNavModel
    assert m.rowCount() == 6
    idx = m.index(0, 0)
    assert m.data(idx, m.AreaIdRole) == m.data(idx, m.DomainIdRole)


def test_workspace_nav_model_when_operations(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    wm = bridge.workspaceNavModel
    assert wm.rowCount() == 8
    idx = wm.index(0, 0)
    assert wm.data(idx, wm.WorkspaceIdRole) == "operations_projects"
