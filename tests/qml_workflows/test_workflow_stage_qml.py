"""QQmlComponent smoke: WorkflowStage + workflowStudio (+ shell stub für Pending-Context)."""

from __future__ import annotations

from pathlib import Path

import pytest

from PySide6.QtCore import QCoreApplication, QObject


def _find_descendant_by_object_name(root: QObject, name: str) -> QObject | None:
    for o in root.findChildren(QObject):
        if o.objectName() == name:
            return o
    return None


@pytest.fixture
def qml_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "qml"
    assert root.is_dir()
    return root


def test_workflow_stage_qml_instantiates(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QObject, Property, QUrl, Slot
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.workflows.workflow_viewmodel import WorkflowStudioViewModel
    from tests.unit.python_bridge.test_workflow_studio_viewmodel import _FakeWorkflowPort

    class _ShellStub(QObject):
        def __init__(self) -> None:
            super().__init__()
            self._pending_context_json = ""

        def _get_p(self) -> str:
            return self._pending_context_json

        def _set_p(self, v: str) -> None:
            self._pending_context_json = v if v is not None else ""

        pendingContextJson = Property(str, _get_p, _set_p)

        @Slot()
        def clearPendingContext(self) -> None:
            self._pending_context_json = ""

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    wf_vm = WorkflowStudioViewModel(port=_FakeWorkflowPort())
    shell = _ShellStub()
    eng.rootContext().setContextProperty("workflowStudio", wf_vm)
    eng.rootContext().setContextProperty("shell", shell)
    path = qml_root / "domains" / "workflows" / "WorkflowStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
    wf_vm.dispose()


def test_workflow_stage_sync_pending_context_clears_shell(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QObject, Property, QUrl, Slot
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.workflows.workflow_viewmodel import WorkflowStudioViewModel
    from tests.unit.python_bridge.test_workflow_studio_viewmodel import _FakeWorkflowPort

    class _ShellStub(QObject):
        def __init__(self) -> None:
            super().__init__()
            self._pending_context_json = ""

        def _get_p(self) -> str:
            return self._pending_context_json

        def _set_p(self, v: str) -> None:
            self._pending_context_json = v if v is not None else ""

        pendingContextJson = Property(str, _get_p, _set_p)

        @Slot()
        def clearPendingContext(self) -> None:
            self._pending_context_json = ""

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    wf_vm = WorkflowStudioViewModel(port=_FakeWorkflowPort())
    shell = _ShellStub()
    shell._pending_context_json = '{"workflow_ops_scope":"project"}'
    eng.rootContext().setContextProperty("workflowStudio", wf_vm)
    eng.rootContext().setContextProperty("shell", shell)
    clears: list[int] = []
    wf_vm.shellPendingContextClearSuggested.connect(lambda: clears.append(1))
    path = qml_root / "domains" / "workflows" / "WorkflowStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
    assert clears == [1]
    assert shell._pending_context_json == ""
    wf_vm.dispose()


def test_workflow_stage_deferred_pending_context_then_resolver(qapplication, qml_root: Path) -> None:
    """graphDirty + select_wf-Kontext: Shell bleibt, bis Resolver + shellPendingContextClearSuggested."""
    from PySide6.QtCore import QObject, Property, QUrl, Slot
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.workflows.workflow_viewmodel import WorkflowStudioViewModel
    from tests.unit.python_bridge.test_workflow_studio_viewmodel import _FakeWorkflowPort

    class _ShellStub(QObject):
        def __init__(self) -> None:
            super().__init__()
            self._pending_context_json = ""

        def _get_p(self) -> str:
            return self._pending_context_json

        def _set_p(self, v: str) -> None:
            self._pending_context_json = v if v is not None else ""

        pendingContextJson = Property(str, _get_p, _set_p)

        @Slot()
        def clearPendingContext(self) -> None:
            self._pending_context_json = ""

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    wf_vm = WorkflowStudioViewModel(port=_FakeWorkflowPort())
    shell = _ShellStub()
    eng.rootContext().setContextProperty("workflowStudio", wf_vm)
    eng.rootContext().setContextProperty("shell", shell)
    wf_vm.requestSelectWorkflow("w1")
    wf_vm.addNode("agent")
    assert wf_vm.graphDirty is True
    shell._pending_context_json = '{"workflow_ops_select_workflow_id":"w2"}'
    clears: list[int] = []
    wf_vm.shellPendingContextClearSuggested.connect(lambda: clears.append(1))
    path = qml_root / "domains" / "workflows" / "WorkflowStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
    assert wf_vm.graphActionPending is True
    assert shell._pending_context_json != ""
    assert clears == []
    wf_vm.resolveGraphActionDiscard()
    assert clears == [1]
    assert shell._pending_context_json == ""
    assert wf_vm.selectedWorkflow == "w2"
    wf_vm.dispose()


def test_workflow_stage_deferred_pending_context_then_resolver_save(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QObject, Property, QUrl, Slot
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.workflows.workflow_viewmodel import WorkflowStudioViewModel
    from tests.unit.python_bridge.test_workflow_studio_viewmodel import _FakeWorkflowPort

    class _ShellStub(QObject):
        def __init__(self) -> None:
            super().__init__()
            self._pending_context_json = ""

        def _get_p(self) -> str:
            return self._pending_context_json

        def _set_p(self, v: str) -> None:
            self._pending_context_json = v if v is not None else ""

        pendingContextJson = Property(str, _get_p, _set_p)

        @Slot()
        def clearPendingContext(self) -> None:
            self._pending_context_json = ""

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    wf_vm = WorkflowStudioViewModel(port=_FakeWorkflowPort())
    shell = _ShellStub()
    eng.rootContext().setContextProperty("workflowStudio", wf_vm)
    eng.rootContext().setContextProperty("shell", shell)
    wf_vm.requestSelectWorkflow("w1")
    wf_vm.addNode("agent")
    shell._pending_context_json = '{"workflow_ops_select_workflow_id":"w2"}'
    clears: list[int] = []
    wf_vm.shellPendingContextClearSuggested.connect(lambda: clears.append(1))
    path = qml_root / "domains" / "workflows" / "WorkflowStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
    assert wf_vm.graphActionPending is True
    wf_vm.resolveGraphActionSave()
    assert clears == [1]
    assert shell._pending_context_json == ""
    assert wf_vm.selectedWorkflow == "w2"
    wf_vm.dispose()


def test_workflow_stage_deferred_pending_context_then_resolver_cancel_keeps_shell_json(
    qapplication, qml_root: Path
) -> None:
    from PySide6.QtCore import QObject, Property, QUrl, Slot
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.workflows.workflow_viewmodel import WorkflowStudioViewModel
    from tests.unit.python_bridge.test_workflow_studio_viewmodel import _FakeWorkflowPort

    class _ShellStub(QObject):
        def __init__(self) -> None:
            super().__init__()
            self._pending_context_json = ""

        def _get_p(self) -> str:
            return self._pending_context_json

        def _set_p(self, v: str) -> None:
            self._pending_context_json = v if v is not None else ""

        pendingContextJson = Property(str, _get_p, _set_p)

        @Slot()
        def clearPendingContext(self) -> None:
            self._pending_context_json = ""

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    wf_vm = WorkflowStudioViewModel(port=_FakeWorkflowPort())
    shell = _ShellStub()
    eng.rootContext().setContextProperty("workflowStudio", wf_vm)
    eng.rootContext().setContextProperty("shell", shell)
    wf_vm.requestSelectWorkflow("w1")
    wf_vm.addNode("agent")
    pending = '{"workflow_ops_select_workflow_id":"w2"}'
    shell._pending_context_json = pending
    clears: list[int] = []
    wf_vm.shellPendingContextClearSuggested.connect(lambda: clears.append(1))
    path = qml_root / "domains" / "workflows" / "WorkflowStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
    assert wf_vm.graphActionPending is True
    wf_vm.resolveGraphActionCancel()
    assert clears == []
    assert shell._pending_context_json == pending
    assert wf_vm.selectedWorkflow == "w1"
    assert wf_vm.graphDirty is True
    wf_vm.dispose()


def test_workflow_json_object_input_block_qml_instantiates(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    path = qml_root / "domains" / "workflows" / "WorkflowJsonObjectInputBlock.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    root = comp.create()
    assert root is not None, comp.errorString()
    root.setProperty("width", 320)
    root.setProperty("areaObjectName", "probeJsonArea")
    root.setProperty("caption", "cap")
    QCoreApplication.processEvents()
    ta = _find_descendant_by_object_name(root, "probeJsonArea")
    assert ta is not None


def test_workflow_stage_test_run_and_rerun_json_areas_not_cross_coupled(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QObject, Property, QUrl, Slot
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.workflows.workflow_viewmodel import WorkflowStudioViewModel
    from tests.unit.python_bridge.test_workflow_studio_viewmodel import _FakeWorkflowPort

    class _ShellStub(QObject):
        def __init__(self) -> None:
            super().__init__()
            self._pending_context_json = ""

        def _get_p(self) -> str:
            return self._pending_context_json

        def _set_p(self, v: str) -> None:
            self._pending_context_json = v if v is not None else ""

        pendingContextJson = Property(str, _get_p, _set_p)

        @Slot()
        def clearPendingContext(self) -> None:
            self._pending_context_json = ""

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    wf_vm = WorkflowStudioViewModel(port=_FakeWorkflowPort())
    shell = _ShellStub()
    eng.rootContext().setContextProperty("workflowStudio", wf_vm)
    eng.rootContext().setContextProperty("shell", shell)
    wf_vm.requestSelectWorkflow("w1")
    path = qml_root / "domains" / "workflows" / "WorkflowStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    stage = comp.create()
    assert stage is not None, comp.errorString()
    ta_test = _find_descendant_by_object_name(stage, "workflowTestRunInputJson")
    ta_rerun = _find_descendant_by_object_name(stage, "workflowRerunOverrideJson")
    assert ta_test is not None and ta_rerun is not None
    wf_vm.setRerunOverrideInputJson('{"rerun_marker": 1}')
    QCoreApplication.processEvents()
    rerun_text = str(ta_rerun.property("text"))
    assert "rerun_marker" in rerun_text
    wf_vm.setTestRunInputJson('{"test_marker_only": true}')
    QCoreApplication.processEvents()
    assert str(ta_rerun.property("text")) == rerun_text
    assert "test_marker_only" not in str(ta_rerun.property("text"))
    wf_vm.dispose()


def test_schedule_read_panel_qml_instantiates(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.workflows.workflow_viewmodel import WorkflowStudioViewModel
    from tests.unit.python_bridge.test_workflow_studio_viewmodel import (
        _FakeScheduleReadPort,
        _FakeWorkflowPort,
    )

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    wf_vm = WorkflowStudioViewModel(port=_FakeWorkflowPort(), schedule_read_port=_FakeScheduleReadPort())
    eng.rootContext().setContextProperty("workflowStudio", wf_vm)
    path = qml_root / "domains" / "workflows" / "ScheduleReadPanel.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
    wf_vm.dispose()


def test_run_history_panel_qml_instantiates(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.workflows.workflow_viewmodel import WorkflowStudioViewModel
    from tests.unit.python_bridge.test_workflow_studio_viewmodel import _FakeWorkflowPort

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    wf_vm = WorkflowStudioViewModel(port=_FakeWorkflowPort())
    eng.rootContext().setContextProperty("workflowStudio", wf_vm)
    path = qml_root / "domains" / "workflows" / "RunHistoryPanel.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
    wf_vm.dispose()
