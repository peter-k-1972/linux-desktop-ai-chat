from __future__ import annotations

import sys
from pathlib import Path

import pytest

from app.ui_runtime.qml.qml_runtime import QmlRuntime
from app.ui_runtime.theme_loader import load_theme_manifest_from_path
from tests.architecture.app_ui_themes_source_root import app_ui_themes_source_root


@pytest.fixture
def qml_manifest_path() -> Path:
    p = (
        app_ui_themes_source_root()
        / "builtins"
        / "light_default"
        / "manifest.json"
    )
    assert p.is_file()
    return p


def test_qml_runtime_activate_loads_root(qml_manifest_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from app.ui_runtime.qml.chat.chat_qml_viewmodel import ChatQmlViewModel
    from tests.qml_chat.test_chat_viewmodel import VmTestPort

    _ = QApplication.instance() or QApplication(sys.argv)
    manifest = load_theme_manifest_from_path(qml_manifest_path)
    chat_vm = ChatQmlViewModel(VmTestPort(), schedule_coro=lambda c: None)
    chat_vm._set_default_model_id("stub")
    rt = QmlRuntime(manifest)
    rt.activate(context={"chat": chat_vm})
    try:
        engine = rt._engine
        assert engine is not None
        roots = engine.rootObjects()
        assert len(roots) == 1
    finally:
        rt.deactivate()
