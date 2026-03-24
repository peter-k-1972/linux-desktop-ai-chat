"""ReleasesPanel — Port-Pfad vs. Legacy (Slice 3 + Batch 4)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.deployment.panels.releases_panel import ReleasesPanel
from app.ui_contracts.workspaces.deployment_releases import (
    CreateDeploymentReleaseCommand,
    DeploymentReleaseCreateWrite,
    DeploymentReleaseEditorSnapshotDto,
    DeploymentReleaseSelectionState,
    DeploymentReleaseTableRowDto,
    DeploymentReleaseUpdateWrite,
    DeploymentReleasesViewState,
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
        self.list_calls = 0
        self.selection_calls = 0
        self.creates = 0
        self.updates = 0
        self.archives = 0

    def load_releases_list_view(self) -> DeploymentReleasesViewState:
        self.list_calls += 1
        r = DeploymentReleaseTableRowDto(
            release_id="p1",
            display_name="FromPort",
            version_label="1",
            lifecycle_status="ready",
            artifact_kind="",
            project_id=None,
        )
        return DeploymentReleasesViewState(phase="ready", rows=(r,), banner_message=None)

    def load_release_selection_state(self, release_id: str | None) -> DeploymentReleaseSelectionState:
        self.selection_calls += 1
        return DeploymentReleaseSelectionState(
            selected_release_id=release_id,
            detail=None,
            history_rows=(),
        )

    def get_release_editor_snapshot(self, release_id: str) -> DeploymentReleaseEditorSnapshotDto | None:
        return DeploymentReleaseEditorSnapshotDto(
            release_id=release_id,
            display_name="FromPort",
            version_label="1",
            artifact_kind="",
            artifact_ref="",
            lifecycle_status="ready",
            project_id=None,
        )

    def create_release(self, write: DeploymentReleaseCreateWrite) -> None:
        self.creates += 1
        del write

    def update_release(self, write: DeploymentReleaseUpdateWrite) -> None:
        self.updates += 1
        del write

    def archive_release(self, release_id: str) -> None:
        self.archives += 1
        del release_id


def test_legacy_panel_refresh_calls_list_releases(qapp, monkeypatch) -> None:
    called: list[str] = []

    class _S:
        def list_releases(self):
            called.append("list")
            return []

    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: _S(),
    )
    p = ReleasesPanel(deployment_releases_port=None)
    p.refresh()
    assert called == ["list"]


def test_port_path_refresh_uses_fake_port(qapp) -> None:
    port = _FakePort()
    p = ReleasesPanel(deployment_releases_port=port)
    p.refresh()
    assert port.list_calls == 1
    assert port.selection_calls >= 1
    assert p._list.rowCount() == 1
    assert p._list.item(0, 0).text() == "FromPort"


def test_port_path_on_new_dispatches_create_command(qapp, monkeypatch) -> None:
    port = _FakePort()
    p = ReleasesPanel(deployment_releases_port=port)
    hc = MagicMock()
    assert p._releases_presenter is not None
    p._releases_presenter.handle_command = hc

    class _Dlg:
        DialogCode = type("DC", (), {"Accepted": 1})()

        def __init__(self, *a, **k) -> None:
            pass

        def exec(self) -> int:
            return 1

        def values(self) -> tuple:
            return ("N", "1.0", "k", "r", None, None)

    monkeypatch.setattr(
        "app.gui.domains.operations.deployment.panels.releases_panel.ReleaseEditDialog",
        _Dlg,
    )
    p._on_new()
    hc.assert_called()
    cmd = hc.call_args[0][0]
    assert isinstance(cmd, CreateDeploymentReleaseCommand)
    assert cmd.write.display_name == "N"
