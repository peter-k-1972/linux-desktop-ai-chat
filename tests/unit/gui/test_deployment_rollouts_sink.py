"""DeploymentRolloutsSink."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QLabel, QTableWidget

from app.core.deployment.models import RolloutOutcome
from app.gui.domains.operations.deployment.deployment_rollouts_sink import DeploymentRolloutsSink
from app.ui_contracts.workspaces.deployment_rollouts import (
    DeploymentRolloutFilterOptionDto,
    DeploymentRolloutTableRowDto,
    DeploymentRolloutsFilterSnapshot,
    DeploymentRolloutsViewState,
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


def _combos(qapp):
    del qapp
    t, r, o, rng = QComboBox(), QComboBox(), QComboBox(), QComboBox()
    t.addItem("(alle Ziele)", None)
    r.addItem("(alle Releases)", None)
    o.addItem("(alle)", None)
    o.addItem("Erfolg", RolloutOutcome.SUCCESS)
    rng.addItem("Alle Zeiten", None)
    rng.addItem("Letzte 7 Tage", 7)
    return t, r, o, rng


def test_sink_loading(qapp) -> None:
    table = QTableWidget()
    table.setColumnCount(7)
    t, r, o, rng = _combos(qapp)
    fb = QLabel()
    sink = DeploymentRolloutsSink(table, t, r, o, rng, fb)
    af = DeploymentRolloutsFilterSnapshot()
    sink.apply_full_state(DeploymentRolloutsViewState(phase="loading", active_filter=af))
    assert fb.isVisible()
    assert table.rowCount() == 0


def test_sink_ready(qapp) -> None:
    table = QTableWidget()
    table.setColumnCount(7)
    t, r, o, rng = _combos(qapp)
    fb = QLabel()
    sink = DeploymentRolloutsSink(table, t, r, o, rng, fb)
    af = DeploymentRolloutsFilterSnapshot(
        target_id="t1",
        release_id="r1",
        outcome=RolloutOutcome.SUCCESS,
        range_preset=7,
    )
    row = DeploymentRolloutTableRowDto(
        recorded_at="t",
        target_display_name="T",
        release_display_name="R",
        version_label="v",
        outcome="success",
        workflow_run_id="w1",
        message="m",
    )
    sink.apply_full_state(
        DeploymentRolloutsViewState(
            phase="ready",
            active_filter=af,
            target_options=(
                DeploymentRolloutFilterOptionDto(None, "(alle Ziele)"),
                DeploymentRolloutFilterOptionDto("t1", "One"),
            ),
            release_options=(
                DeploymentRolloutFilterOptionDto(None, "(alle Releases)"),
                DeploymentRolloutFilterOptionDto("r1", "Rel"),
            ),
            table_rows=(row,),
        ),
    )
    assert not fb.isVisible()
    assert t.currentData() == "t1"
    assert r.currentData() == "r1"
    assert table.rowCount() == 1
    assert table.item(0, 5).data(Qt.ItemDataRole.UserRole) == "w1"


def test_sink_error(qapp) -> None:
    table = QTableWidget()
    table.setColumnCount(7)
    t, r, o, rng = _combos(qapp)
    fb = QLabel()
    sink = DeploymentRolloutsSink(table, t, r, o, rng, fb)
    af = DeploymentRolloutsFilterSnapshot()
    sink.apply_full_state(
        DeploymentRolloutsViewState(
            phase="error",
            active_filter=af,
            error=SettingsErrorInfo(code="c", message="oops"),
        ),
    )
    assert "oops" in fb.text()
    assert table.rowCount() == 0
