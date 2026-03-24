"""Smoke: Foundation Theme (LibraryTheme + strukturierte Theme-API) lädt ohne QML-Fehler."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


@pytest.fixture
def qml_manifest_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    p = root / "app" / "ui_themes" / "builtins" / "light_default" / "manifest.json"
    assert p.is_file()
    return p


def test_theme_singleton_exposes_structured_api(monkeypatch) -> None:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from app.ui_runtime.qml.chat.chat_qml_viewmodel import ChatQmlViewModel
    from tests.qml_chat.test_chat_viewmodel import VmTestPort

    _ = QGuiApplication.instance() or QGuiApplication(sys.argv)

    root = Path(__file__).resolve().parents[2]
    qml_root = root / "qml"
    engine = QQmlEngine()
    engine.addImportPath(str(qml_root))

    chat_vm = ChatQmlViewModel(VmTestPort(), schedule_coro=lambda c: None)
    engine.rootContext().setContextProperty("chat", chat_vm)

    probe = qml_root / "foundation" / "_smoke" / "ThemeStructuredProbe.qml"
    comp = QQmlComponent(engine, QUrl.fromLocalFile(str(probe.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
    assert obj.property("ok") is True
    obj.deleteLater()


def test_settings_stage_loads_foundation_preview(qml_manifest_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    _ = QGuiApplication.instance() or QGuiApplication(sys.argv)
    root = Path(__file__).resolve().parents[2]
    qml_root = root / "qml"
    engine = QQmlEngine()
    engine.addImportPath(str(qml_root))

    stage = qml_root / "domains" / "settings" / "SettingsStagePlaceholder.qml"
    comp = QQmlComponent(engine, QUrl.fromLocalFile(str(stage.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()
    obj.deleteLater()
