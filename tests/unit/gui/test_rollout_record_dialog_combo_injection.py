"""RolloutRecordDialog — injizierte Combos ohne Service (POST-CORRECTION Slice 1)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.deployment.dialogs.rollout_record_dialog import RolloutRecordDialog
from app.ui_contracts.workspaces.deployment_rollouts import RolloutRecordComboRowDto, RolloutRecordComboSnapshot


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_injected_snapshot_populates_combos(qapp: QApplication) -> None:
    snap = RolloutRecordComboSnapshot(
        targets=(RolloutRecordComboRowDto("t1", "Target One"),),
        ready_releases=(RolloutRecordComboRowDto("r1", "Release A (1.0)"),),
    )
    d = RolloutRecordDialog(None, combo_snapshot=snap)
    assert d._target.count() == 1
    assert d._target.itemData(0) == "t1"
    assert d._release.count() == 1
    assert d._release.itemData(0) == "r1"
    tid, rid, *_rest = d.values()
    assert tid == "t1"
    assert rid == "r1"
