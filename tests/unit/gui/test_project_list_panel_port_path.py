"""ProjectListPanel — Slice-1-Portpfad."""

from __future__ import annotations

from app.gui.domains.operations.projects.panels.project_list_panel import ProjectListPanel
from app.ui_contracts.workspaces.projects_overview import (
    ActiveProjectSnapshot,
    ProjectListItem,
    ProjectListLoadResult,
    SubscriptionHandle,
)


class _Port:
    def __init__(self) -> None:
        self.filter_calls: list[str] = []

    def load_project_list(
        self,
        filter_text: str,
        *,
        active_project_id: int | None = None,
        selected_project_id: int | None = None,
    ) -> ProjectListLoadResult:
        del active_project_id, selected_project_id
        self.filter_calls.append(filter_text)
        items = (
            ProjectListItem(
                project_id=1,
                display_name="Projekt A",
                secondary_text="A-1",
                lifecycle_label="Aktiv",
                status_label="active",
                last_activity_label="01.01.2026 10:00",
                is_active=False,
                is_selected=False,
            ),
            ProjectListItem(
                project_id=2,
                display_name="Projekt B",
                secondary_text="B-1",
                lifecycle_label="Planung",
                status_label="draft",
                last_activity_label="02.01.2026 10:00",
                is_active=True,
                is_selected=False,
            ),
        )
        return ProjectListLoadResult(items=items)

    def load_active_project_snapshot(self) -> ActiveProjectSnapshot:
        return ActiveProjectSnapshot(active_project_id=2, is_any_project_active=True)

    def subscribe_active_project_changed(self, listener):
        del listener
        return SubscriptionHandle()


def test_project_list_panel_uses_port_and_emits_project_id(qapplication) -> None:
    port = _Port()
    panel = ProjectListPanel(read_port=port)
    selected: list[object] = []
    panel.project_selected.connect(selected.append)

    panel.refresh()

    assert panel._table.rowCount() == 2
    assert port.filter_calls
    assert panel._table.item(0, 0).data(0x0100) == 1
    panel._table.selectRow(1)
    assert selected[-1] == 2
    panel.deleteLater()


def test_project_list_panel_filter_path_uses_presenter(qapplication) -> None:
    port = _Port()
    panel = ProjectListPanel(read_port=port)

    panel._filter.setText("abc")

    assert port.filter_calls[-1] == "abc"
    panel.deleteLater()
