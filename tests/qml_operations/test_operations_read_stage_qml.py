"""QQmlComponent smoke: OperationsReadStage + operationsRead."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def qml_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "qml"
    assert root.is_dir()
    return root


def test_operations_read_stage_qml_instantiates(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.operations.operations_read_viewmodel import build_operations_read_viewmodel

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    vm = build_operations_read_viewmodel()
    eng.rootContext().setContextProperty("operationsRead", vm)
    path = qml_root / "domains" / "operations" / "OperationsReadStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
    assert obj.objectName() == "operationsReadStage"
    vm.dispose()
