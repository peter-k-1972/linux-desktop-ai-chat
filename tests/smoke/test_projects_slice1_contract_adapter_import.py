"""Smoke: Projects Slice 1 Vertrags- und Adapterbasis importierbar."""


def test_import_stack() -> None:
    from app.gui.domains.operations.projects.project_inspector_sink import ProjectInspectorSink
    from app.gui.domains.operations.projects.project_overview_sink import ProjectOverviewSink
    from app.ui_application.presenters.project_inspector_presenter import ProjectInspectorPresenter
    from app.ui_application.adapters.service_projects_overview_command_adapter import (
        ServiceProjectsOverviewCommandAdapter,
    )
    from app.ui_application.adapters.service_projects_overview_read_adapter import (
        ServiceProjectsOverviewReadAdapter,
    )
    from app.ui_application.presenters.project_overview_presenter import ProjectOverviewPresenter
    from app.ui_application.ports.projects_overview_command_port import ProjectsOverviewCommandPort
    from app.ui_application.ports.projects_overview_host_callbacks import ProjectsOverviewHostCallbacks
    from app.ui_application.ports.projects_overview_read_port import ProjectsOverviewReadPort
    from app.ui_contracts.workspaces.projects_overview import ProjectOverviewState

    assert ProjectInspectorSink.__name__ == "ProjectInspectorSink"
    assert ProjectOverviewSink.__name__ == "ProjectOverviewSink"
    assert ProjectInspectorPresenter.__name__ == "ProjectInspectorPresenter"
    assert ServiceProjectsOverviewReadAdapter.__name__ == "ServiceProjectsOverviewReadAdapter"
    assert ServiceProjectsOverviewCommandAdapter.__name__ == "ServiceProjectsOverviewCommandAdapter"
    assert ProjectOverviewPresenter.__name__ == "ProjectOverviewPresenter"
    assert ProjectsOverviewReadPort.__name__ == "ProjectsOverviewReadPort"
    assert ProjectsOverviewCommandPort.__name__ == "ProjectsOverviewCommandPort"
    assert ProjectsOverviewHostCallbacks.__name__ == "ProjectsOverviewHostCallbacks"
    assert ProjectOverviewState.__name__ == "ProjectOverviewState"
