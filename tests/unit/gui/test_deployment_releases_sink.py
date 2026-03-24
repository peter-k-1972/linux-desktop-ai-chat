"""DeploymentReleasesSink."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QTableWidget

from app.gui.domains.operations.deployment.deployment_releases_sink import DeploymentReleasesSink
from app.ui_contracts.workspaces.deployment_releases import (
    DeploymentReleaseDetailDto,
    DeploymentReleaseHistoryRowDto,
    DeploymentReleaseTableRowDto,
    DeploymentReleasesViewState,
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


def _tables(qapp) -> tuple[QTableWidget, QTableWidget, QLabel, QLabel]:
    del qapp
    lt = QTableWidget()
    lt.setColumnCount(5)
    ht = QTableWidget()
    ht.setColumnCount(5)
    return lt, ht, QLabel(), QLabel()


def test_sink_loading(qapp) -> None:
    lt, ht, det, fb = _tables(qapp)
    sink = DeploymentReleasesSink(lt, ht, det, fb)
    sink.apply_full_state(DeploymentReleasesViewState(phase="loading", rows=()))
    assert fb.isVisible()
    assert lt.rowCount() == 0
    assert ht.rowCount() == 0


def test_sink_ready_rows_and_detail(qapp) -> None:
    lt, ht, det, fb = _tables(qapp)
    sink = DeploymentReleasesSink(lt, ht, det, fb)
    row = DeploymentReleaseTableRowDto(
        release_id="rid",
        display_name="N",
        version_label="v",
        lifecycle_status="ready",
        artifact_kind="oci",
        project_id=2,
    )
    d = DeploymentReleaseDetailDto(
        display_name="N",
        version_label="v",
        lifecycle_status="ready",
        artifact_ref="aref",
        artifact_kind="ak",
    )
    h = DeploymentReleaseHistoryRowDto(
        recorded_at="t",
        target_display_name="T1",
        outcome="success",
        workflow_run_id="w1",
        message="m",
    )
    sink.apply_full_state(
        DeploymentReleasesViewState(
            phase="ready",
            rows=(row,),
            detail=d,
            history_rows=(h,),
            selected_release_id="rid",
        ),
    )
    assert not fb.isVisible()
    assert lt.rowCount() == 1
    assert lt.item(0, 0).text() == "N"
    assert lt.item(0, 0).data(Qt.ItemDataRole.UserRole) == "rid"
    assert "aref" in det.text()
    assert ht.rowCount() == 1
    assert ht.item(0, 3).data(Qt.ItemDataRole.UserRole) == "w1"


def test_sink_error(qapp) -> None:
    lt, ht, det, fb = _tables(qapp)
    sink = DeploymentReleasesSink(lt, ht, det, fb)
    sink.apply_full_state(
        DeploymentReleasesViewState(
            phase="error",
            rows=(),
            error=SettingsErrorInfo(code="c", message="oops"),
        ),
    )
    assert "oops" in fb.text()
    assert lt.rowCount() == 0


def test_sink_ready_shows_banner(qapp) -> None:
    lt, ht, det, fb = _tables(qapp)
    sink = DeploymentReleasesSink(lt, ht, det, fb)
    row = DeploymentReleaseTableRowDto(
        release_id="r",
        display_name="N",
        version_label="v",
        lifecycle_status="ready",
        artifact_kind="",
        project_id=None,
    )
    sink.apply_full_state(
        DeploymentReleasesViewState(
            phase="ready",
            rows=(row,),
            banner_message=SettingsErrorInfo(code="v", message="validation failed"),
        ),
    )
    assert fb.isVisible()
    assert "validation failed" in fb.text()
    assert lt.rowCount() == 1
