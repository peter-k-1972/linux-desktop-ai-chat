"""QQmlComponent smoke: AgentStage + agentStudio context."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def qml_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "qml"
    assert root.is_dir()
    return root


def test_agent_stage_qml_instantiates(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.agents.agent_viewmodel import build_agent_viewmodel

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    eng.rootContext().setContextProperty("agentStudio", build_agent_viewmodel())
    path = qml_root / "domains" / "agents" / "AgentStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()


def test_agent_viewmodel_dispatch_requires_selection(qapplication) -> None:
    from python_bridge.agents.agent_viewmodel import AgentViewModel

    class _Port:
        def refresh_registry(self) -> None:
            pass

        def list_all_profiles(self):
            return []

        def get_profile(self, _aid: str):
            return None

    vm = AgentViewModel(port=_Port())
    vm.dispatchTask("hello")
    assert vm.tasks.rowCount() == 0
