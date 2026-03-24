from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QUrl

from app.ui_runtime.qml.shell_bridge_facade import ShellBridgeFacade


@pytest.fixture
def qml_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "qml"
    assert root.is_dir()
    return root


def test_shell_initial_domain_and_url(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    assert bridge.activeDomain == "chat"
    assert bridge.shellReady is True
    assert bridge.stageUrl.isValid()
    assert "ChatStage.qml" in bridge.stageUrl.toLocalFile()


def test_shell_invalid_domain_ignored(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    before = bridge.activeDomain
    url_before = bridge.stageUrl
    bridge.requestDomainChange("not_a_domain")
    assert bridge.activeDomain == before
    assert bridge.stageUrl == url_before


def test_shell_navigate_round_trip(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestDomainChange("settings")
    assert bridge.activeDomain == "settings"
    assert "domains/settings/SettingsStage.qml" in bridge.stageUrl.toLocalFile()
    bridge.requestDomainChange("chat")
    assert bridge.activeDomain == "chat"


def test_shell_workflows_stage_url(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestDomainChange("workflows")
    assert bridge.activeDomain == "workflows"
    assert "domains/workflows/WorkflowStage.qml" in bridge.stageUrl.toLocalFile()


def test_shell_prompt_studio_stage_url(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestDomainChange("prompt_studio")
    assert bridge.activeDomain == "prompt_studio"
    assert "domains/prompts/PromptStage.qml" in bridge.stageUrl.toLocalFile()


def test_shell_agent_tasks_stage_url(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestDomainChange("agent_tasks")
    assert bridge.activeDomain == "agent_tasks"
    assert "domains/agents/AgentStage.qml" in bridge.stageUrl.toLocalFile()


def test_shell_deployment_stage_url(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestDomainChange("deployment")
    assert bridge.activeDomain == "deployment"
    assert "domains/deployment/DeploymentStage.qml" in bridge.stageUrl.toLocalFile()


def test_shell_settings_stage_url(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestDomainChange("settings")
    assert bridge.activeDomain == "settings"
    assert "domains/settings/SettingsStage.qml" in bridge.stageUrl.toLocalFile()


def test_shell_projects_stage_url(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    bridge.initialize()
    bridge.requestDomainChange("projects")
    assert bridge.activeDomain == "projects"
    assert "domains/projects/ProjectStage.qml" in bridge.stageUrl.toLocalFile()


def test_domain_nav_model_row_count(qapplication, qml_root: Path) -> None:
    bridge = ShellBridgeFacade(qml_root)
    m = bridge.domainNavModel
    assert m.rowCount() == 7
    idx = m.index(0, 0)
    assert m.data(idx, m.DomainIdRole) == "chat"
    assert m.data(idx, m.LabelRole) == "Chat"
