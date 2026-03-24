"""QQmlComponent smoke: ProjectStage + projectStudio (Stub ProjectService)."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def qml_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "qml"
    assert root.is_dir()
    return root


def test_project_stage_qml_instantiates(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.projects.project_viewmodel import ProjectViewModel

    class _Stub:
        def list_projects(self, filter_text: str = ""):
            return [
                {
                    "project_id": 1,
                    "name": "Stub-Projekt",
                    "description": "",
                    "status": "active",
                    "lifecycle_status": "active",
                }
            ]

        def get_project_monitoring_snapshot(self, project_id: int):
            return {"message_count_7d": 0, "last_activity_at": None}

        def get_project(self, project_id: int):
            return {
                "project_id": project_id,
                "name": "Stub-Projekt",
                "description": "Test",
                "default_context_policy": None,
                "status": "active",
                "lifecycle_status": "active",
            }

        def set_active_project(self, project_id=None, project=None):
            return None

        def create_project(self, name: str, description: str = ""):
            return 2

        def delete_project(self, project_id: int):
            return None

        def get_recent_chats_of_project(self, project_id: int, limit: int = 8):
            return []

        def list_files_of_project(self, project_id: int, limit: int = 40):
            return []

        def list_workflows_for_project(self, project_id: int, *, limit: int):
            return []

        def list_active_agents_for_project(self, project_id: int):
            return []

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    vm = ProjectViewModel(port=_Stub())
    eng.rootContext().setContextProperty("projectStudio", vm)
    path = qml_root / "domains" / "projects" / "ProjectStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
