"""TargetsPanel — Port-Pfad sendet Mutations-Commands an den Presenter (Batch 4)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.deployment.panels.targets_panel import TargetsPanel
from app.ui_contracts.workspaces.deployment_targets import (
    CreateDeploymentTargetCommand,
    DeploymentTargetCreateWrite,
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


def test_port_path_on_new_dispatches_create_command(qapp, monkeypatch) -> None:
    class _FakePort:
        pass

    p = TargetsPanel(deployment_targets_port=_FakePort())
    hc = MagicMock()
    assert p._targets_presenter is not None
    p._targets_presenter.handle_command = hc

    class _Dlg:
        DialogCode = type("DC", (), {"Accepted": 1})()

        def __init__(self, *a, **k) -> None:
            pass

        def exec(self) -> int:
            return 1

        def values(self) -> tuple:
            return ("N", "kind", "notes", 3)

    monkeypatch.setattr(
        "app.gui.domains.operations.deployment.panels.targets_panel.TargetEditDialog",
        _Dlg,
    )
    p._on_new()
    hc.assert_called()
    cmd = hc.call_args[0][0]
    assert isinstance(cmd, CreateDeploymentTargetCommand)
    assert cmd.write == DeploymentTargetCreateWrite(
        name="N",
        kind="kind",
        notes="notes",
        project_id=3,
    )
