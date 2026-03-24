"""TargetsPanel — Port-Pfad vs. Legacy refresh."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.deployment.panels.targets_panel import TargetsPanel
from app.ui_contracts.workspaces.deployment_targets import (
    CreateDeploymentTargetCommand,
    DeploymentTargetCreateWrite,
    DeploymentTargetTableRowDto,
    DeploymentTargetsViewState,
    UpdateDeploymentTargetCommand,
    DeploymentTargetUpdateWrite,
)


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


class _FakePort:
    def __init__(self) -> None:
        self.calls = 0
        self.creates = 0
        self.updates = 0

    def load_targets_view(self) -> DeploymentTargetsViewState:
        self.calls += 1
        r = DeploymentTargetTableRowDto(
            target_id="p1",
            name="FromPort",
            kind="",
            project_id=None,
            last_rollout_recorded_at="—",
            last_rollout_outcome="—",
        )
        return DeploymentTargetsViewState(
            phase="ready",
            rows=(r,),
            error=None,
            banner_message=None,
        )

    def get_target_editor_snapshot(self, target_id: str):
        from app.ui_contracts.workspaces.deployment_targets import DeploymentTargetEditorSnapshotDto

        return DeploymentTargetEditorSnapshotDto(
            target_id=target_id,
            name="X",
            kind="",
            notes="",
            project_id=None,
        )

    def create_target(self, write) -> None:  # noqa: ANN001
        self.creates += 1
        del write

    def update_target(self, write) -> None:  # noqa: ANN001
        self.updates += 1
        del write


def test_legacy_panel_no_port_calls_refresh_without_presenter(qapp, monkeypatch) -> None:
    called: list[str] = []

    class _S:
        def get_last_rollout_per_target(self):
            return {}

        def list_targets(self):
            called.append("list")
            return []

    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: _S(),
    )
    p = TargetsPanel(deployment_targets_port=None)
    p.refresh()
    assert called == ["list"]


def test_port_path_refresh_uses_fake_port(qapp) -> None:
    port = _FakePort()
    p = TargetsPanel(deployment_targets_port=port)
    p.refresh()
    assert port.calls == 1
    assert p._table.rowCount() == 1
    assert p._table.item(0, 0).text() == "FromPort"


def test_port_path_create_command_wires_through_presenter(qapp) -> None:
    port = _FakePort()
    p = TargetsPanel(deployment_targets_port=port)
    assert p._targets_presenter is not None
    p._targets_presenter.handle_command(
        CreateDeploymentTargetCommand(DeploymentTargetCreateWrite(name="n")),
    )
    assert port.creates == 1
    assert port.calls >= 1


def test_port_path_update_command_wires_through_presenter(qapp) -> None:
    port = _FakePort()
    p = TargetsPanel(deployment_targets_port=port)
    p._targets_presenter.handle_command(
        UpdateDeploymentTargetCommand(
            DeploymentTargetUpdateWrite(target_id="p1", name="Z"),
        ),
    )
    assert port.updates == 1
