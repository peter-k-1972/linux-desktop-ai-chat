"""RolloutsPanel — Port-Pfad vs. Legacy (Slice 4)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.deployment.panels.rollouts_panel import RolloutsPanel
from app.ui_contracts.workspaces.deployment_rollouts import (
    DeploymentRolloutFilterOptionDto,
    DeploymentRolloutRecordMutationResult,
    DeploymentRolloutTableRowDto,
    DeploymentRolloutsFilterSnapshot,
    DeploymentRolloutsViewState,
    RecordDeploymentRolloutCommand,
    RolloutRecordComboRowDto,
    RolloutRecordComboSnapshot,
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
        self.record_combo_calls = 0
        self.record_commands: list[RecordDeploymentRolloutCommand] = []

    def load_rollouts_view(self, filter_snapshot: DeploymentRolloutsFilterSnapshot) -> DeploymentRolloutsViewState:
        self.calls += 1
        row = DeploymentRolloutTableRowDto(
            recorded_at="t",
            target_display_name="T",
            release_display_name="R",
            version_label="v",
            outcome="success",
            workflow_run_id="",
            message="",
        )
        return DeploymentRolloutsViewState(
            phase="ready",
            active_filter=filter_snapshot,
            target_options=(DeploymentRolloutFilterOptionDto(None, "(alle Ziele)"),),
            release_options=(DeploymentRolloutFilterOptionDto(None, "(alle Releases)"),),
            table_rows=(row,),
        )

    def load_rollout_record_combo_options(self) -> RolloutRecordComboSnapshot:
        self.record_combo_calls += 1
        return RolloutRecordComboSnapshot(
            targets=(RolloutRecordComboRowDto("tid", "Target A"),),
            ready_releases=(RolloutRecordComboRowDto("rid", "Rel (v)"),),
        )

    def record_deployment_rollout(
        self,
        command: RecordDeploymentRolloutCommand,
    ) -> DeploymentRolloutRecordMutationResult:
        self.record_commands.append(command)
        return DeploymentRolloutRecordMutationResult(ok=True)


def test_legacy_refresh_calls_service(qapp, monkeypatch) -> None:
    called: list[str] = []

    class _S:
        def list_targets(self):
            called.append("targets")
            return []

        def list_releases(self):
            called.append("releases")
            return []

        def list_rollouts(self, flt):  # noqa: ANN001
            called.append("rollouts")
            return []

    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: _S(),
    )
    p = RolloutsPanel(deployment_rollouts_port=None)
    p.refresh()
    assert "targets" in called
    assert "rollouts" in called


def test_port_path_refresh_uses_fake_port(qapp) -> None:
    port = _FakePort()
    p = RolloutsPanel(deployment_rollouts_port=port)
    p.refresh()
    assert port.calls == 1
    assert p._table.rowCount() == 1


def test_port_path_on_record_calls_port_record_and_refreshes(qapp, monkeypatch) -> None:
    class _StubDialog:
        DialogCode = type("DC", (), {"Accepted": 1})()

        def __init__(self, parent, *, combo_snapshot=None) -> None:
            del parent, combo_snapshot

        def exec(self) -> int:
            return 1

        def values(self) -> tuple:
            return ("tid", "rid", "success", "", None, None, None)

    monkeypatch.setattr(
        "app.gui.domains.operations.deployment.panels.rollouts_panel.RolloutRecordDialog",
        _StubDialog,
    )
    port = _FakePort()
    p = RolloutsPanel(deployment_rollouts_port=port)
    loads_before = port.calls
    p._on_record()
    assert len(port.record_commands) == 1
    assert port.record_commands[0].target_id == "tid"
    assert port.record_commands[0].release_id == "rid"
    assert port.calls == loads_before + 1


def test_port_path_on_record_injects_combo_snapshot(qapp, monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _StubDialog:
        class DialogCode:
            Accepted = 1

        def __init__(self, parent, *, combo_snapshot=None) -> None:
            captured["combo_snapshot"] = combo_snapshot

        def exec(self) -> int:
            return 0

    monkeypatch.setattr(
        "app.gui.domains.operations.deployment.panels.rollouts_panel.RolloutRecordDialog",
        _StubDialog,
    )
    port = _FakePort()
    p = RolloutsPanel(deployment_rollouts_port=port)
    p._on_record()
    assert port.record_combo_calls == 1
    snap = captured.get("combo_snapshot")
    assert snap is not None
    assert snap.targets[0].value_id == "tid"
    assert snap.ready_releases[0].label == "Rel (v)"
