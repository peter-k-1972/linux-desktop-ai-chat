"""QQmlComponent smoke: DeploymentStage + deploymentStudio (Stub-Service)."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def qml_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "qml"
    assert root.is_dir()
    return root


def test_deployment_stage_qml_instantiates(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.deployment.deployment_viewmodel import DeploymentViewModel

    class _Stub:
        def list_releases(self):
            return []

        def get_release(self, _rid: str):
            return None

        def list_targets(self):
            return []

        def update_release(self, **_kw):
            raise AssertionError("not used in smoke")

        def record_rollout(self, **_kw):
            raise AssertionError("not used in smoke")

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    vm = DeploymentViewModel(port=_Stub())
    eng.rootContext().setContextProperty("deploymentStudio", vm)
    path = qml_root / "domains" / "deployment" / "DeploymentStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
