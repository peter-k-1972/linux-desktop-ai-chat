"""ProjectInspectorPanel — Slice-1-Portpfad."""

from __future__ import annotations

from app.gui.domains.operations.projects.panels.project_inspector_panel import ProjectInspectorPanel
from app.ui_contracts.workspaces.projects_overview import ProjectInspectorState


class _Port:
    def __init__(self, state: ProjectInspectorState | None = None) -> None:
        self.state = _state() if state is None else state
        self.load_calls: list[int] = []

    def load_project_inspector(self, project_id: int) -> ProjectInspectorState | None:
        self.load_calls.append(project_id)
        return self.state


def _state(project_id: int = 42) -> ProjectInspectorState:
    return ProjectInspectorState(
        project_id=project_id,
        title="Testprojekt",
        status_label="active",
        lifecycle_label="Aktiv",
        context_policy_caption="Architektur",
        context_rules_narrative="Regel A\nRegel B",
        description_display="Beschreibung",
        customer_name="Acme",
        internal_code="AC-42",
        external_reference="REF-42",
        updated_at_label="31.03.2026 13:00",
    )


def test_project_inspector_panel_uses_port_path(qapplication) -> None:
    port = _Port()
    panel = ProjectInspectorPanel(read_port=port)

    panel.set_project({"project_id": 42, "name": "Testprojekt"})

    assert port.load_calls == [42]
    assert panel._empty.isHidden()
    assert panel._name.text() == "Testprojekt"
    assert panel._desc.text() == "Beschreibung"
    assert panel._rules.text() == "Regel A\nRegel B"
    assert panel._mode.text() == "Architektur"
    panel.deleteLater()


def test_project_inspector_panel_shows_empty_state(qapplication) -> None:
    panel = ProjectInspectorPanel(read_port=_Port())

    panel.set_project(None)

    assert panel._empty.text() == "Kein Projekt gewählt."
    assert panel._name.isHidden()
    panel.deleteLater()


def test_project_inspector_panel_shows_missing_project_message(qapplication) -> None:
    port = _Port()
    port.state = None
    panel = ProjectInspectorPanel(read_port=port)

    panel.set_project({"project_id": 42})

    assert panel._empty.text() == "Projekt konnte nicht geladen werden."
    assert panel._name.isHidden()
    panel.deleteLater()


def test_project_inspector_panel_refresh_uses_current_selection(qapplication) -> None:
    port = _Port()
    panel = ProjectInspectorPanel(read_port=port)
    panel.set_project({"project_id": 42})

    panel.refresh()

    assert port.load_calls == [42, 42]
    panel.deleteLater()
