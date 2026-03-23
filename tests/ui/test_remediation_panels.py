"""
GUI-Regression nach Remediation: CC Tools/Data Stores, Dashboard, Prompt-Vorschau.

Nutzt QApplication + processEvents (kein zwingendes pytest-qt/qtbot).
"""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QPushButton, QTableWidget

from app.gui.domains.control_center.panels.tools_panels import ToolRegistryPanel
from app.gui.domains.control_center.panels.data_stores_panels import DataStoreOverviewPanel
from app.gui.domains.dashboard.panels.system_status_panel import SystemStatusPanel
from app.gui.domains.dashboard.panels.qa_status_panel import QAStatusPanel
from app.gui.domains.operations.prompt_studio.panels.prompt_editor_panel import PromptEditorPanel
from app.gui.domains.operations.prompt_studio.panels.preview_panel import PromptPreviewPanel


@pytest.mark.ui
@pytest.mark.regression
def test_tool_registry_panel_live_rows_not_dummy_table(qapplication):
    panel = ToolRegistryPanel()
    panel.show()
    QApplication.processEvents()
    table = panel.findChild(QTableWidget)
    assert table is not None
    assert table.rowCount() == 4
    assert table.item(0, 0).text() == "filesystem_tools"
    panel.refresh()
    QApplication.processEvents()
    assert table.rowCount() == 4
    btn = panel.findChild(QPushButton)
    assert btn is not None
    assert "Aktualisieren" in btn.text() or btn.text() != ""


@pytest.mark.ui
@pytest.mark.regression
def test_data_store_overview_three_rows(qapplication):
    panel = DataStoreOverviewPanel()
    panel.show()
    QApplication.processEvents()
    table = panel.findChild(QTableWidget)
    assert table is not None
    assert table.rowCount() == 3
    stores = {table.item(i, 0).text() for i in range(3)}
    assert "Chat / App-DB" in stores
    assert "RAG / Vektor-Index" in stores


@pytest.mark.ui
@pytest.mark.regression
def test_system_status_panel_refresh_no_exception(qapplication):
    panel = SystemStatusPanel()
    panel.show()
    QApplication.processEvents()
    panel.refresh()
    QApplication.processEvents()
    assert panel._status is not None
    assert "Ollama" in panel._status.text()


@pytest.mark.ui
@pytest.mark.regression
def test_qa_status_panel_loads_inventory_counts(qapplication):
    from app.qa.dashboard_adapter import DashboardData, ExecutiveStatus

    data = DashboardData()
    data.executive = ExecutiveStatus(
        test_count=99,
        prioritized_gaps=0,
        orphan_backlog=0,
        last_verification="",
        qa_health="ok",
    )
    mock_inst = MagicMock()
    mock_inst.load.return_value = data
    with patch("app.qa.dashboard_adapter.QADashboardAdapter") as mock_cls:
        mock_cls.return_value = mock_inst
        panel = QAStatusPanel()
    panel.show()
    QApplication.processEvents()
    assert "99" in panel._detail.text()


@pytest.mark.ui
@pytest.mark.regression
def test_prompt_editor_emits_state_for_preview(qapplication):
    editor = PromptEditorPanel()
    preview = PromptPreviewPanel()
    editor.show()
    preview.show()
    QApplication.processEvents()
    received = []

    def on_state(title, body):
        received.append((title, body))

    editor.editor_state_changed.connect(on_state)
    editor._name.setText("T1")
    editor._content.setPlainText("Hallo")
    QApplication.processEvents()
    assert received
    last_title, last_body = received[-1]
    assert last_title == "T1"
    assert "Hallo" in last_body
    preview.on_editor_state(last_title, last_body)
    assert "Hallo" in preview._body.toPlainText()
