"""DeploymentTargetsSink."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QTableWidget

from app.gui.domains.operations.deployment.deployment_targets_sink import DeploymentTargetsSink
from app.ui_contracts.workspaces.deployment_targets import (
    DeploymentTargetTableRowDto,
    DeploymentTargetsViewState,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


def test_sink_loading(qapp) -> None:
    table = QTableWidget()
    table.setColumnCount(5)
    fb = QLabel()
    sink = DeploymentTargetsSink(table, fb)
    sink.apply_full_state(DeploymentTargetsViewState(phase="loading", rows=()))
    assert fb.isVisible()
    assert table.rowCount() == 0


def test_sink_ready_rows(qapp) -> None:
    table = QTableWidget()
    table.setColumnCount(5)
    fb = QLabel()
    sink = DeploymentTargetsSink(table, fb)
    row = DeploymentTargetTableRowDto(
        target_id="x",
        name="N",
        kind="k",
        project_id=2,
        last_rollout_recorded_at="t",
        last_rollout_outcome="ok",
    )
    sink.apply_full_state(DeploymentTargetsViewState(phase="ready", rows=(row,)))
    assert not fb.isVisible()
    assert table.rowCount() == 1
    assert table.item(0, 0).text() == "N"


def test_sink_error(qapp) -> None:
    table = QTableWidget()
    table.setColumnCount(5)
    fb = QLabel()
    sink = DeploymentTargetsSink(table, fb)
    sink.apply_full_state(
        DeploymentTargetsViewState(
            phase="error",
            rows=(),
            error=SettingsErrorInfo(code="c", message="oops"),
            banner_message=None,
        ),
    )
    assert "oops" in fb.text()
    assert table.rowCount() == 0


def test_sink_ready_with_banner_keeps_rows(qapp) -> None:
    table = QTableWidget()
    table.setColumnCount(5)
    fb = QLabel()
    sink = DeploymentTargetsSink(table, fb)
    row = DeploymentTargetTableRowDto(
        target_id="t",
        name="N",
        kind="",
        project_id=None,
        last_rollout_recorded_at="—",
        last_rollout_outcome="—",
    )
    sink.apply_full_state(
        DeploymentTargetsViewState(
            phase="ready",
            rows=(row,),
            error=None,
            banner_message=SettingsErrorInfo(code="v", message="check input"),
        ),
    )
    assert "check input" in fb.text()
    assert fb.isVisible()
    assert table.rowCount() == 1
