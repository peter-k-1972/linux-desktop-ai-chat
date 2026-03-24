"""SettingsModelRoutingSink — Qt-Widgets."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QSpinBox

from app.core.models.roles import ModelRole
from app.gui.domains.settings.settings_model_routing_sink import SettingsModelRoutingSink
from app.ui_contracts.workspaces.settings_model_routing import ModelRoutingStudioState


@pytest.fixture(scope="module")
def qapplication():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_sink_apply_full_state(qapplication) -> None:
    assistant = QComboBox()
    assistant.addItem("A", "id-a")
    assistant.addItem("B", "id-b")
    ar = QCheckBox()
    cloud = QCheckBox()
    cvl = QCheckBox()
    ws = QCheckBox()
    ok = QCheckBox()
    role = QComboBox()
    for r in (ModelRole.DEFAULT, ModelRole.CODE):
        role.addItem(str(r.value), r)
    temp = QDoubleSpinBox()
    temp.setRange(0, 2)
    mt = QSpinBox()
    mt.setRange(0, 32768)
    top_p = QDoubleSpinBox()
    top_p.setRange(0, 1)
    top_p.setSingleStep(0.05)
    timeout = QSpinBox()
    timeout.setRange(0, 300)
    retry = QCheckBox()
    stc = QCheckBox()
    sink = SettingsModelRoutingSink(
        assistant,
        ar,
        cloud,
        cvl,
        ws,
        ok,
        role,
        temp,
        top_p,
        mt,
        timeout,
        retry,
        stc,
    )
    sink.apply_full_state(
        ModelRoutingStudioState(
            model="id-b",
            auto_routing=False,
            cloud_escalation=True,
            cloud_via_local=False,
            web_search=True,
            overkill_mode=False,
            default_role="CODE",
            temperature=1.2,
            top_p=0.85,
            max_tokens=8000,
            llm_timeout_seconds=120,
            retry_without_thinking=False,
            chat_streaming_enabled=False,
            error=None,
        ),
    )
    assert assistant.currentData() == "id-b"
    assert ar.isChecked() is False
    assert cloud.isChecked() is True
    assert temp.value() == 1.2
    assert top_p.value() == 0.85
    assert mt.value() == 8000
    assert timeout.value() == 120
    assert retry.isChecked() is False
    assert stc.isChecked() is False
